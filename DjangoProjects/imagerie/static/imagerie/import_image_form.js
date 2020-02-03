$(document).ready(() => {
        $('#id_form-TOTAL_FORMS').val(1);

        function remove_line() {
            let id = this.id.split('-');
            id = parseInt(id[id.length - 1]);
            let total_form = $('#id_form-TOTAL_FORMS');
            let max = parseInt(total_form.val());
            let tr = this.parentElement.parentElement;
            tr.parentElement.removeChild(tr);
            for (let i = id; i < max - 1; i++) {
                let tr = $(`#tr-id_form-${i + 1}`);
                let new_html = tr.html().replace(/id_form-\d+/g, `id_form-${i}`);
                new_html = new_html.replace(/form-\d+/g, `form-${i}`);
                tr.html(new_html);
                tr.attr('id', `tr-id_form-${i}`)
            }
            $('.remove_btn').click(remove_line);
            total_form.val(max - 1);
        }

        $('#add_more').click(function () {
            let form_idx = $('#id_form-TOTAL_FORMS').val();
            $('#forms').append($('#empty_form').html().replace(/__prefix__/g, form_idx));
            $('#id_form-TOTAL_FORMS').val(parseInt(form_idx) + 1);
            $('#remove-id_form-' + form_idx).click(remove_line);
        });

        $('#remove-id_form-0').click(remove_line);
    }
);
