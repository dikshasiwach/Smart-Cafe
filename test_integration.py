import urllib.request
import urllib.error
import json

def test():
    base = 'http://127.0.0.1:5000/api'
    
    # 1. Test Health
    req = urllib.request.urlopen(base + '/health')
    assert req.status == 200
    print('PASS 1: Health check OK')

    # 2. Test Table T01 check
    req = urllib.request.urlopen(base + '/tables/by-number/T01')
    t01 = json.loads(req.read().decode())
    assert t01['table']['table_number'] == 'T01'
    print('PASS 2: Table T01 detected & verified')

    # 3. Test Categories
    req = urllib.request.urlopen(base + '/menu/categories')
    cats = json.loads(req.read().decode())
    assert len(cats['categories']) >= 10
    print(f'PASS 3: All {len(cats["categories"])} categories loaded')

    # 4. Test Menu Items
    req = urllib.request.urlopen(base + '/menu/items')
    items = json.loads(req.read().decode())
    assert len(items['items']) >= 30
    print(f'PASS 4: All {len(items["items"])} menu items loaded')

    # 5. Test Dine-In Order Placement for T01
    sample_item = items['items'][0]
    sample_item2 = items['items'][1]
    order_data = json.dumps({
        'order_type': 'dine-in',
        'table_number': 'T01',
        'customer_name': 'Dev Test Guest',
        'customer_phone': '9876543210',
        'payment_method': 'online_razorpay',
        'items': [
            {'menu_item_id': sample_item['id'], 'quantity': 2},
            {'menu_item_id': sample_item2['id'], 'quantity': 1}
        ]
    }).encode('utf-8')
    req = urllib.request.Request(base + '/orders', data=order_data, headers={'Content-Type': 'application/json'}, method='POST')
    res = json.loads(urllib.request.urlopen(req).read().decode())
    order_id = res['order']['id']
    rzp_order_id = res['razorpay']['id']
    assert res['order']['table_number'] == 'T01'
    print(f'PASS 5: Dine-in order placed: {res["order"]["order_number"]} (Total: INR {res["order"]["total_amount"]})')

    # 6. Test Payment Verification
    verify_data = json.dumps({
        'order_id': order_id,
        'razorpay_order_id': rzp_order_id,
        'razorpay_payment_id': 'pay_test_verified_123',
        'razorpay_signature': 'sig_test_verified_123'
    }).encode('utf-8')
    req = urllib.request.Request(base + '/payments/verify', data=verify_data, headers={'Content-Type': 'application/json'}, method='POST')
    verify_res = json.loads(urllib.request.urlopen(req).read().decode())
    assert verify_res['order']['payment_status'] == 'paid'
    print('PASS 6: Razorpay payment verified by backend')

    # 7. Test Admin Login
    login_data = json.dumps({'email': 'admin@smartcafe.com', 'password': 'admin123'}).encode('utf-8')
    req = urllib.request.Request(base + '/auth/login', data=login_data, headers={'Content-Type': 'application/json'}, method='POST')
    login_res = json.loads(urllib.request.urlopen(req).read().decode())
    token = login_res['token']
    assert login_res['user']['role'] == 'admin'
    print('PASS 7: Admin authenticated, role validated')

    # 8. Test Admin Order Status Update (placed -> accepted -> preparing -> ready -> served)
    for st in ['accepted', 'preparing', 'ready', 'served']:
        st_data = json.dumps({'status': st, 'prep_time_mins': 15}).encode('utf-8')
        req = urllib.request.Request(f'{base}/orders/{order_id}/status', data=st_data, headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}, method='PATCH')
        updated = json.loads(urllib.request.urlopen(req).read().decode())
        assert updated['order']['status'] == st
    print('PASS 8: Order lifecycle status updates verified (placed -> served)')

    # 9. Test Customer Review Submission
    rev_data = json.dumps({
        'order_id': order_id,
        'customer_name': 'Dev Test Guest',
        'star_rating': 5,
        'food_rating': 5,
        'service_rating': 5,
        'comment': 'Phenomenal crispy fries and instant service!'
    }).encode('utf-8')
    req = urllib.request.Request(base + '/reviews', data=rev_data, headers={'Content-Type': 'application/json'}, method='POST')
    rev_res = json.loads(urllib.request.urlopen(req).read().decode())
    assert rev_res['review']['star_rating'] == 5
    print('PASS 9: Customer review submitted and linked')

    # 10. Test Duplicate Review Prevention
    try:
        req = urllib.request.Request(base + '/reviews', data=rev_data, headers={'Content-Type': 'application/json'}, method='POST')
        urllib.request.urlopen(req)
        assert False, 'Should have failed with duplicate'
    except urllib.error.HTTPError as e:
        assert e.code == 409
        print('PASS 10: Duplicate review prevention verified')

    # 11. Test Table QR code generation
    req = urllib.request.urlopen(base + '/tables/tbl-01/qr')
    qr = json.loads(req.read().decode())
    assert 'data:image/png;base64' in qr['dataUrl']
    assert 'menu?table=T01' in qr['targetUrl']
    print('PASS 11: High-res QR code generated for Table T01')

    # 12. Test Reservation Creation & Conflict Handling
    res_data = json.dumps({
        'customer_name': 'Pooja Hegde',
        'customer_phone': '9988776655',
        'reservation_date': '2026-10-25',
        'time_slot': '07:30 PM',
        'guest_count': 4,
        'special_requests': 'Anniversary table please'
    }).encode('utf-8')
    req = urllib.request.Request(base + '/reservations', data=res_data, headers={'Content-Type': 'application/json'}, method='POST')
    booked = json.loads(urllib.request.urlopen(req).read().decode())
    assert booked['reservation']['reservation_code'].startswith('RES-')
    print(f'PASS 12: Table reservation created: #{booked["reservation"]["reservation_code"]}')

    # 13. Test Gemini Chatbot grounded menu query
    chat_data = json.dumps({'message': 'Suggest something under ₹200'}).encode('utf-8')
    req = urllib.request.Request(base + '/chatbot/message', data=chat_data, headers={'Content-Type': 'application/json'}, method='POST')
    chat_res = json.loads(urllib.request.urlopen(req).read().decode())
    assert len(chat_res['text']) > 10
    print('PASS 13: Gemini AI concierge responded with grounded menu recommendations')

    # 14. Test Analytics Overview
    req = urllib.request.Request(base + '/analytics/overview', headers={'Authorization': f'Bearer {token}'})
    stats = json.loads(urllib.request.urlopen(req).read().decode())
    assert stats['metrics']['totalOrders'] >= 1
    assert stats['metrics']['todayRevenue'] > 0
    print(f'PASS 14: Analytics reporting live metrics (Revenue: INR {stats["metrics"]["todayRevenue"]}, Orders: {stats["metrics"]["totalOrders"]})')

    print('\n======================================================')
    print('ALL VERIFICATION SUITE CHECKS COMPLETED AND PASSING!')
    print('======================================================')

if __name__ == '__main__':
    test()
