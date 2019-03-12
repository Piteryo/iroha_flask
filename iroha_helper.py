from irohalib import IrohaCrypto
import binascii
from irohalib import Iroha, IrohaGrpc
import os
import json

class IrohaHelper:
    def __init__(self, admin_key, iroha, net):
        self.admin_private_key = admin_key
        self.iroha = iroha 
        self.net = net
        self.accounts = {}
        self.accounts['fabric'] = self.new_user('fabric', ['pharmacy'], ['good'])
        self.accounts['office'] = self.new_user('office', ['government'], ['corruptcoin'])
        self.accounts['pharmacy'] = self.new_user('pharmacy', ['office'], ['corruptcoin', 'good'])
        self.accounts['government'] = self.new_user('government', [], ['corruptcoin'])


    def new_user(self, user_id, peer_user_ids, coins):
        result = ''
        if not os.path.exists(user_id + '@test.priv'):
            private_key = IrohaCrypto.private_key()
            result = {
                    'id': user_id,
                    'key': private_key.decode('ascii'),
                    'peer_users': peer_user_ids,
                    'coins': coins
                }
            with open(user_id + '@test.priv', 'w+') as f:
                json.dump(result, f)
        else:
            with open(user_id + "@test.priv", 'r') as f:
                result = json.load(f)
        return result


    def create_domain_and_asset(self):
        """
        Creates asset 'coin#test' with precision 2
        """
        commands = [
            self.iroha.command('CreateAsset', asset_name='good',
                        domain_id='test', precision=2),
            self.iroha.command('CreateAsset', asset_name='corruptcoin',
                        domain_id='test', precision=2)
        ]
        tx = IrohaCrypto.sign_transaction(
            self.iroha.transaction(commands), self.admin_private_key)
        self.send_transaction_and_print_status(tx)


    def send_transaction_and_print_status(self, transaction):
        hex_hash = binascii.hexlify(IrohaCrypto.hash(transaction))
        print('Transaction hash = {}, creator = {}'.format(
            hex_hash, transaction.payload.reduced_payload.creator_account_id))
        self.net.send_tx(transaction)
        res = ''
        for status in self.net.tx_status_stream(transaction):
            print(status)
            res += str(status) + '\n'
        return res


    def add_coin_to_admin(self):
        """
        Add 1000.00 units of 'coin#test' to 'admin@test'
        """
        tx = self.iroha.transaction([
            self.iroha.command('AddAssetQuantity',
                        asset_id='corruptcoin#test', amount='1000.00'),
            self.iroha.command('AddAssetQuantity',
                        asset_id='good#test', amount='1000.00')
        ])
        IrohaCrypto.sign_transaction(tx, self.admin_private_key)
        self.send_transaction_and_print_status(tx)
        tx = self.iroha.transaction([
            self.iroha.command('TransferAsset',
                        src_account_id='admin@test',
                        dest_account_id=self.accounts['fabric']['id'] + "@test",
                        asset_id='good#test',
                        description='init top up',
                        amount='500.00'),

            self.iroha.command('TransferAsset',
                        src_account_id='admin@test',
                        dest_account_id=self.accounts['pharmacy']['id'] + "@test",
                        asset_id='corruptcoin#test',
                        description='init top up',
                        amount='500.00')
        ])
        IrohaCrypto.sign_transaction(tx, self.admin_private_key)
        self.send_transaction_and_print_status(tx)


    def create_accounts(self):
        """
        Create account 'userone@domain'
        """
        transactions = []
        for account in self.accounts.keys():
            transactions.append(self.iroha.command('CreateAccount', account_name=account, domain_id='test',
                        public_key=IrohaCrypto.derive_public_key(self.accounts[account]['key'])))
        tx = self.iroha.transaction(transactions)

        IrohaCrypto.sign_transaction(tx, self.admin_private_key)
        self.send_transaction_and_print_status(tx)
    
    # def grant_permissions(self):
    #     self.iroha.transaction([
    #         self.iroha.command('GrantPermission', account_id=fabric['id'], permission=primitive_pb2.can_transfer_my_assets)
    #     ], creator_account=fabric['id'])

    #     IrohaCrypto.sign_transaction(tx, fabric['key'])
    #     send_transaction_and_print_status(tx)


    #     self.iroha.transaction([
    #         self.iroha.command('GrantPermission', account_id=office['id'], permission=primitive_pb2.can_transfer_my_assets)
    #     ], creator_account=office['id'])

    #     IrohaCrypto.sign_transaction(tx, office['key'])
    #     send_transaction_and_print_status(tx)


    #     self.iroha.transaction([
    #         self.iroha.command('GrantPermission', account_id=pharmacy['id'], permission=primitive_pb2.can_transfer_my_assets)
    #     ], creator_account=pharmacy['id'])

    #     IrohaCrypto.sign_transaction(tx, pharmacy['key'])
    #     send_transaction_and_print_status(tx)


    #     self.iroha.transaction([
    #         self.iroha.command('GrantPermission', account_id=government['id'], permission=primitive_pb2.can_transfer_my_assets)
    #     ], creator_account=government['id'])

    #     IrohaCrypto.sign_transaction(tx, government['key'])
    #     send_transaction_and_print_status(tx)


    def transfer_coin_from_user_to_user(self, from_name, to_name, amount, coin):
        """
        Transfer 2.00 'coin#domain' from 'admin@test' to 'userone@domain'
        """
        iroha_local = Iroha(from_name + '@test')
        tx = iroha_local.transaction([
            iroha_local.command('TransferAsset', src_account_id=from_name + '@test', dest_account_id = to_name + '@test',
                        asset_id=coin + '#test', description='top up', amount=str(amount))
        ])
        IrohaCrypto.sign_transaction(tx, self.accounts[from_name]['key'])
        return self.send_transaction_and_print_status(tx)


    def userone_grants_to_admin_set_account_detail_permission(self):
        """
        Make admin@test able to set detail to userone@domain
        """
        tx = self.iroha.transaction([
            self.iroha.command('GrantPermission', account_id='admin@test',
                        permission=can_set_my_account_detail)
        ], creator_account='userone@domain')
        IrohaCrypto.sign_transaction(tx, user_private_key)
        self.send_transaction_and_print_status(tx)

    def get_coin_info(self, coin):
        """
        Get asset info for coin#domain
        :return:
        """
        query = self.iroha.query('GetAssetInfo', asset_id=coin +'#domain')
        IrohaCrypto.sign_query(query, self.admin_private_key)

        response = self.net.send_query(query)
        data = response.asset_response.asset
        print('Asset id = {}, precision = {}'.format(data.asset_id, data.precision))


    def get_account_assets(self, account_name):
        """
        List all the assets of account_name
        """

        #iroha_local = Iroha(account_name + '@test')
        query = self.iroha.query('GetAccountAssets', account_id=account_name + "@test")
        IrohaCrypto.sign_query(query, self.admin_private_key)

        response = self.net.send_query(query)
        data = response.account_assets_response.account_assets  
        assets = {asset_name: 0 for asset_name in self.accounts[account_name]['coins']}
        for asset in data:
            assets[asset.asset_id.split('#')[0]] = asset.balance
        return assets