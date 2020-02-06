$(document).ready(() => {
        $('#id_fast_q_name-TOTAL_FORMS').val(1);

        function remove_line() {
            let id = this.id.split('-');
            id = parseInt(id[id.length - 1]);
            let total_form = $('#id_fast_q_name-TOTAL_FORMS');
            let max = parseInt(total_form.val());
            let p = this.parentElement;
            p.parentElement.removeChild(p);
            for (let i = id; i < max - 1; i++) {
                let p = $(`#p-id_fast_q_name-${i + 1}`);
                let new_html = p.html().replace(/id_fast_q_name-\d+/g, `id_fast_q_name-${i}`);
                new_html = new_html.replace(/fast_q_name-\d+/g, `fast_q_name-${i}`);
                p.html(new_html);
                p.attr('id', `p-id_fast_q_name-${i}`)
            }
            $('.remove_btn').click(remove_line);
            total_form.val(max - 1);
        }

        $('#add_more').click(function () {
            let form_idx = $('#id_fast_q_name-TOTAL_FORMS').val();
            $('#forms').append($('#empty_form').html().replace(/__prefix__/g, form_idx));
            $('#id_fast_q_name-TOTAL_FORMS').val(parseInt(form_idx) + 1);
            $('#remove-id_fast_q_name-' + form_idx).click(remove_line);
        });
    }
);