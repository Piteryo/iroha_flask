from irohalib import IrohaCrypto
import binascii

class IrohaHelper:
    def __init__(self, admin_key, iroha, net):
        self.admin_private_key = admin_key
        self.iroha = iroha 
        self.net = net



    def create_domain_and_asset(self):
        """
        Creates domain 'domain' and asset 'coin#domain' with precision 2
        """
        commands = [
            self.iroha.command('CreateDomain', domain_id='domain', default_role='user'),
            self.iroha.command('CreateAsset', asset_name='coin',
                        domain_id='domain', precision=2)
        ]
        tx = IrohaCrypto.sign_transaction(
            self.iroha.transaction(commands), self.admin_private_key)
        self.send_transaction_and_print_status(tx)


    def send_transaction_and_print_status(self, transaction):
        hex_hash = binascii.hexlify(IrohaCrypto.hash(transaction))
        print('Transaction hash = {}, creator = {}'.format(
            hex_hash, transaction.payload.reduced_payload.creator_account_id))
        self.net.send_tx(transaction)
        for status in self.net.tx_status_stream(transaction):
            print(status)


    def add_coin_to_admin(self):
        """
        Add 1000.00 units of 'coin#domain' to 'admin@test'
        """
        tx = self.iroha.transaction([
            self.iroha.command('AddAssetQuantity',
                        asset_id='coin#domain', amount='1000.00')
        ])
        IrohaCrypto.sign_transaction(tx, self.admin_private_key)
        self.send_transaction_and_print_status(tx)


    def create_account(self, name, key):
        """
        Create account 'userone@domain'
        """
        tx = self.iroha.transaction([
            self.iroha.command('CreateAccount', account_name=name, domain_id='domain',
                        public_key=key)
        ])
        IrohaCrypto.sign_transaction(tx, self.admin_private_key)
        self.send_transaction_and_print_status(tx)


    def transfer_coin_from_user_to_user(self, from_name, to_name, amount):
        """
        Transfer 2.00 'coin#domain' from 'admin@test' to 'userone@domain'
        """
        tx = self.iroha.transaction([
            self.iroha.command('TransferAsset', src_account_id=from_name + '@test', dest_account_id = to_name + '@test',
                        asset_id='coin#domain', description='top up', amount=amount)
        ])
        IrohaCrypto.sign_transaction(tx, self.admin_private_key)
        self.send_transaction_and_print_status(tx)


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

    def get_coin_info(self):
        """
        Get asset info for coin#domain
        :return:
        """
        query = self.iroha.query('GetAssetInfo', asset_id='coin#domain')
        IrohaCrypto.sign_query(query, self.admin_private_key)

        response = self.net.send_query(query)
        data = response.asset_response.asset
        print('Asset id = {}, precision = {}'.format(data.asset_id, data.precision))


    def get_account_assets(self, account_name):
        """
        List all the assets of account_name
        """
        query = self.iroha.query('GetAccountAssets', account_id=account_name)
        IrohaCrypto.sign_query(query, self.admin_private_key)

        response = self.net.send_query(query)
        data = response.account_assets_response.account_assets  
        info = ''
        for asset in data:
            info += 'Asset id = {}, balance = {}'.format(
                asset.asset_id, asset.balance) + '\n'

        return info