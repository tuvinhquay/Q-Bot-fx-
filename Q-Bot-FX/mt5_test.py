import MetaTrader5 as mt5

print("Initializing MT5...")

if not mt5.initialize():
    print("INIT FAILED")
    print(mt5.last_error())
else:
    print("INIT SUCCESS")

    info = mt5.account_info()

    if info:
        print("LOGIN:", info.login)
        print("SERVER:", info.server)
        print("BALANCE:", info.balance)
    else:
        print("ACCOUNT INFO FAILED")

    mt5.shutdown()