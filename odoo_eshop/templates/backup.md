register.hmtl

        {% if not session.get('captcha_ok', False)%}
            <tr>
                <th>
                    <label for="account_captcha" class="control-label">{{ _('Captcha') }} (*)</label>
                </th>
                <td>
                    <input type="text" class="form-control account_data" name="captcha">
                </td>
                <td colspan="100%">
                    <img src="data:image/png;base64,{{ captcha_data }}"/>
                </td>
            </tr>
        {% endif %}

            <tr>
                <th>
                    <label for="account_captcha" class="control-label">{{ _('Captcha') }} (*)</label>
                </th>
                <td>
                    <input type="text" class="form-control account_data" name="captcha">
                </td>
                <td>
                    <img src="data:image/png;base64,{{ captcha_data }}"/>
                </td>
            </tr>
