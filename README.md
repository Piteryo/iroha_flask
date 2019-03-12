# iroha_flask
Simple demonstration of iroha app with flask server. 
This example was created for the ``` Basics of Grid and Cloud Computing course. ```

You can find more detailed information in the [presentation](https://docs.google.com/presentation/d/1-h2iDga_xvNEWnKMH_MFAfZjpPHJInWwcvbBH1li2Bk/edit?usp=sharing).
Also you can find demo there.


## How to launch
1. Run ``` ./init_postgres.sh ```
2. Run ``` ./run_node.sh fabric 1 ```
3. Inside opened container run ``` irohad --config fabric_config.docker --genesis_block genesis.block --keypair_name node0 ```
4. Run ``` python app.py ``` in new terminal
5. You can access api by ```127.0.0.1:50051/getuserinfo?account_name=[fabric|office|pharmacy|government] ```


