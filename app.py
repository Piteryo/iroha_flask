import iroha
from iroha_helper import IrohaHelper


from irohalib import Iroha, IrohaGrpc
from irohalib import IrohaCrypto
import binascii

from flask import Flask, request, jsonify

app = Flask(__name__)
iroha = Iroha('admin@test')
net = IrohaGrpc()
irohaHelper = IrohaHelper('f101537e319568c765b2cc89698325604991dca57b9716b58016b253506cab70', iroha, net)

def initialize_iroha():
    user_private_key = IrohaCrypto.private_key()
    user_public_key = IrohaCrypto.derive_public_key(user_private_key)

    irohaHelper.create_domain_and_asset()
    irohaHelper.add_coin_to_admin()
    irohaHelper.create_account('fabric', user_public_key)   


initialize_iroha()

@app.route("/getAccountInfo", methods=["GET"])
def get_info():
    account_name = request.args.get("account_name")
    if is_string_nil_or_empty(account_name):
        return json_response(False, "Please send your account name", {}, 404)
    else:
        return irohaHelper.get_account_assets(account_name + '@test')

    #     response = MessageToDict(IrohaHelper.get_account(account_name))
    #     # in case we don't have account_name on network
    #     if "errorResponse" in response and response["errorResponse"]["reason"] == "NO_ACCOUNT":
    #         user_kp = iroha.ModelCrypto().generateKeypair()
    #         is_success = IrohaHelper.create_account_with_100_coin(account_name, user_kp)
    #         if is_success:
    #             account_id = account_name + "@moneyforward"
    #             IrohaHelper.grant_can_transfer_my_assets_permission_to_admin(account_id, user_kp)
    #             return json_response(is_success, "Created Account Successfully", \
    #                 {"public_key": user_kp.publicKey().hex(), "balance": 100}, 200)
    #         else:
    #             return json_response(is_success, "Can't create account", {}, 501)
    #     else:
    #         response = IrohaHelper.get_account_asset(account_name)
    #         assets_response = MessageToDict(response)["accountAssetsResponse"]
    #         balance = assets_response["accountAssets"][-1]["balance"]
    #         return json_response(True, "", {"balance": balance}, 200)


@app.route("/sendCoinsToUser", methods=["POST"])
def send_coins_to_user():
    fromUser = request.form['username_from']
    toUser = request.form['username_to']
    amount = request.form['amount']
    irohaHelper.transfer_coin_from_user_to_user(fromUser, toUser, amount)



def json_response(is_success, message, data, status_code):
    result = {
        "is_success": is_success,
        "message": message,
        "data": data
    }
    resp = jsonify(result)
    resp.status_code = status_code
    return resp

def is_string_nil_or_empty(string):
    if string is None or len(string) == 0:
        return True
    return False
    # user_private_key = IrohaCrypto.private_key()
    # user_public_key = IrohaCrypto.derive_public_key(user_private_key)