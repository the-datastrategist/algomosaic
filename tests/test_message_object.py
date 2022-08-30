from algom.utils import message_object


def test_message():
    msg = message_object.send(
        msg='Testing 1, 2, 3.',
        channel="#etsting"
    )
    assert msg.response == 'ok'
