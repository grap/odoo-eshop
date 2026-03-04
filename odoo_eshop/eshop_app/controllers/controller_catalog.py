from flask import flash, jsonify, render_template, request

from ..application import app
from ..models.models import execute_odoo_command, get_odoo_object
from ..models.res_partner import get_current_partner_id
from ..models.sale_order import set_quantity, get_current_product_qty
from ..tools.auth import requires_auth
from ..tools.web import redirect_url_for


# ############################################################################
# Catalog (Tree View) Routes
# ############################################################################
@app.route("/catalog_tree/", defaults={"category_id": False})
@app.route("/catalog_tree/<int:category_id>")
def catalog_tree(category_id):
    category_ids = execute_odoo_command(
        "eshop.category",
        "search",
        [
            ("parent_id", "=", category_id),
        ],
    )

    # Get Products
    product_ids = execute_odoo_command(
        "product.product",
        "search",
        [
            ("eshop_state", "=", "available"), 
            ("eshop_category_id", "=", category_id),
        ],
        order="name",
    )

    parent_categories = []
    parent = get_odoo_object("eshop.category", category_id)
    # Get Parent Categories
    while parent:
        parent_categories.insert(0, {"id": parent.id, "name": parent.name})
        parent = get_odoo_object("eshop.category", parent.parent_id)

    return render_template(
        "catalog_tree.html",
        parent_categories=parent_categories,
        category_ids=category_ids,
        product_ids=product_ids,
    )


# ############################################################################
# Catalog (Inline View) Routes
# ############################################################################
@app.route("/catalog_inline/")
@requires_auth
def catalog_inline():
    catalog_inline = execute_odoo_command(
        "product.product", "get_current_eshop_product_list", get_current_partner_id()
    )
    return render_template(
        "catalog_inline.html",
        catalog_inline=catalog_inline,
    )


@app.route("/catalog_inline_quantity_update", methods=["POST"])
def catalog_inline_quantity_update():
    res = set_quantity(
        int(request.form["product_id"]), request.form["new_quantity"], True, "set"
    )
    # Handling AJAX call
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(result=res)
    # Fallback if ever
    flash(res["messages"], res["state"])
    return redirect_url_for("catalog_inline")


# ############################################################################
# Product Routes
# ############################################################################
@app.route("/product/<int:product_id>", methods=['GET', 'POST']) 
def product(product_id):
    # Get Products
    product = get_odoo_object("product.product", product_id)
    product_qty = get_current_product_qty(product_id)

    # Get Parent Categories
    parent_categories = []
    parent = get_odoo_object("eshop.category", product.eshop_category_id)
    while parent:
        parent_categories.insert(0, {"id": parent.id, "name": parent.name})
        parent = get_odoo_object("eshop.category", parent.parent_id)

    return render_template(
        "product.html", product_id=product_id, product_qty=product_qty, parent_categories=parent_categories
    )

# Call by JS AJAX adjustQty
@app.route("/product_adjust_qty", methods=['POST']) 
def product_adjust_qty():
    res = set_quantity(
        int(request.form["product_id"]), request.form["new_quantity"], True, "set"
    )
    # Handling AJAX call
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(result=res)
    import pdb; pdb.set_trace()
    # Fallback if ever
    flash(res["messages"], res["state"])
    return redirect_url_for("product", product_id=product_id, product_qty=new_quantity)


# Call by HTML Form for new product
@app.route("/product_add_new/<int:product_id>", methods=["POST"])
def product_add_new(product_id):
    product = get_odoo_object("product.product", product_id)
    qty = str(product.eshop_minimum_qty or 1)
    # todo : deprecated code that handle qty as string ? 
    res = set_quantity(int(product_id), qty, True, "add")
    flash(res["message"], res["state"])
    return redirect_url_for("product", product_id=product_id)
