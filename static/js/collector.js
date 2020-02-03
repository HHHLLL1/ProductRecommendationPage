function add_impression(user_id, item_id, rating, type, csrf_token) {
            $.ajax({
                 type: 'POST',
                 url: '/collect/log/',
                 data: {
                        "csrfmiddlewaretoken": csrf_token,
                        "user_id": user_id,
                        "item_id": item_id,
                        "rating": rating,
                        "type": type
                        },
                 fail: function(){
                     console.log('log failed(' + rating + ')')
                    }
            })};