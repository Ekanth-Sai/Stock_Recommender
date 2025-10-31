from data_fetchers import get_dhan_fetcher

def test_dhan_oi():
    fetcher = get_dhan_fetcher()
    
    print("\n=== Testing NIFTY OI PCR ===")
    nifty_pcr = fetcher.calculate_oi_pcr('NIFTY')
    print(f"NIFTY PCR: {nifty_pcr}")
    
    print("\n=== Testing BANKNIFTY OI PCR ===")
    banknifty_pcr = fetcher.calculate_oi_pcr('BANKNIFTY')
    print(f"BANKNIFTY PCR: {banknifty_pcr}")
    
    print("\n=== Testing ATM PCR ===")
    atm_data = fetcher.get_atm_strike_pcr('NIFTY')
    if atm_data:
        print(f"ATM PCR: {atm_data['atm_pcr']:.4f}")
        print(f"Strikes considered: {atm_data['strikes_considered']}")

if __name__ == "__main__":
    test_dhan_oi()