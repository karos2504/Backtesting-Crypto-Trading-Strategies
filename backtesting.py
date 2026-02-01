def run(exchange: str, symbol: str, strategy: str, timeframe: str, start_time: int, end_time: int):
    
    if strategy == 'obv':
        hdf5_client = Hdf5Client(exchange)
        df = hdf5_client.get_data(symbol, start_time, end_time)
        df = resample_timeframe(df, timeframe)
        
        
    
