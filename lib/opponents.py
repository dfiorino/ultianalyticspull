def Standardize(df_in):
    """Max and standardize opponent names"""
    # Fix Opponent Name
    opp_list_orig = df_in.Opponent.unique()
    opp_list_found=[]
    for opp_name, match_func, in OPP_MATCH_DICT.items():
        found_matches = match_func(df_in)
        opp_list_found+=list(df_in[found_matches].Opponent.unique())
        df_in.loc[found_matches,'Opponent'] = opp_name
    # Sanity check
    if sorted(opp_list_found) != sorted(opp_list_orig):
        print('All Opponents:',sorted(opp_list_orig))
        print('Search found matches for:',sorted(opp_list_found))
        print('Missing a match for:',[i for i in opp_list_orig if i not in opp_list_found])
        print('Matched twice:', {x:duplicates(opp_list_found, x) for x in set(opp_list_found) if opp_list_found.count(x) > 1 })
    
    return df_in


def MatchAtl(df):
    return df.Opponent.str.contains('atl',case=False)
def MatchAus(df):
    return df.Opponent.str.contains('austin',case=False)
def MatchCha(df):
    return df.Opponent.str.contains('charlotte',case=False)
def MatchChi(df):
    return df.Opponent.str.contains('chicago',case=False) | df.Opponent.str.contains('wildfire',case=False)
def MatchCin(df):
    return df.Opponent.str.contains('cin',case=False) | df.Opponent.str.contains('revolution',case=False)
def MatchDal(df):
    return df.Opponent.str.contains('dallas',case=False)
def MatchDet(df):
    return df.Opponent.str.contains('det',case=False) | df.Opponent.str.contains('mech',case=False)
def MatchDC(df):
    return df.Opponent.str.contains('DC') | df.Opponent.str.contains('breeze',case=False)
def MatchInd(df):
    return df.Opponent.str.contains('Ind') | df.Opponent.str.contains('All')
def MatchJax(df):
    return df.Opponent.str.contains('jack',case=False)
def MatchLA(df):
    return df.Opponent.str.contains('LA') | df.Opponent.str.contains('aviators',case=False)
def MatchMad(df):
    return df.Opponent.str.contains('madison',case=False) | df.Opponent.str.contains('radicals',case=False)
def MatchMin(df):
    return df.Opponent.str.contains('Mn') | df.Opponent.str.contains('min',case=False) | df.Opponent.str.contains('wind',case=False)
def MatchMon(df):
    return df.Opponent.str.contains('Mont',case=False) | df.Opponent.str.contains('mtl royal',case=False)
def MatchNsh(df):
    return df.Opponent.str.contains('nash',case=False) | df.Opponent.str.contains('night',case=False)
def MatchNY(df):
    return df.Opponent.str.contains('york',case=False) | df.Opponent.str.contains('empire',case=False)
def MatchOtt(df):
    return df.Opponent.str.contains('ottawa',case=False) | df.Opponent.str.contains('outlaws',case=False)
def MatchPit(df):
    return df.Opponent.str.contains('pit',case=False) | df.Opponent.str.contains('thunder',case=False)
def MatchPhl(df):
    return df.Opponent.str.contains('phil',case=False) | df.Opponent.str.contains('phoe',case=False)
def MatchRal(df):
    return df.Opponent.str.contains('Ral')
def MatchRoc(df):
    return df.Opponent.str.contains('dragon',case=False) | df.Opponent.str.contains('roch',case=False)
def MatchSLC(df):
    return df.Opponent.str.contains('salt lake',case=False) | df.Opponent.str.contains('lions',case=False)
def MatchSD(df):
    return df.Opponent.str.contains('san diego',case=False) | df.Opponent.str.contains('growlers',case=False) | df.Opponent.str.startswith('Sd')
def MatchSF(df):
    return df.Opponent.str.contains('fran',case=False) | df.Opponent.str.contains('flame',case=False) | (df.Opponent.str.lower()=='sf')
def MatchSJ(df):
    return df.Opponent.str.contains('sj',case=False) | df.Opponent.str.contains('spiders',case=False) | df.Opponent.str.contains('san jose',case=False)
def MatchSeaC(df):
    return df.Opponent.str.contains('seat',case=False) & df.Opponent.str.contains('casc',case=False)
def MatchSeaR(df):
    return df.Opponent.str.contains('seat',case=False) & df.Opponent.str.contains('rap',case=False)
def MatchTor(df):
    return df.Opponent.str.contains('rush',case=False) | df.Opponent.str.contains('toronto',case=False)
def MatchTB(df):
    return df.Opponent.str.contains('tampa',case=False) & (df.Opponent.str.contains('bay',case=False)|df.Opponent.str.contains('cannons',case=False))
def MatchVan(df):
    return df.Opponent.str.contains('vancouver',case=False)

OPP_MATCH_DICT ={
            'Atlanta Hustle':MatchAtl,
            'Austin Sol':MatchAus,
            'Charlotte Express':MatchCha,
            'Chicago Wildfire':MatchChi,
            'Cincinnati Revolution':MatchCin,
            'Dallas Roughnecks':MatchDal,
            'Detroit Mechanix':MatchDet,
            'DC Breeze':MatchDC,
            'Indianapolis AlleyCats':MatchInd,
            'Jacksonville Cannons':MatchJax,
            'Los Angeles Aviators':MatchLA,
            'Madison Radicals':MatchMad,
            'Minnesota Wind Chill':MatchMin,
            'Montreal Royal':MatchMon,
            'Nashville NightWatch':MatchNsh,
            'New York Empire':MatchNY,
            'Ottawa Outlaws':MatchOtt,
            'Pittsburgh Thunderbirds':MatchPit,
            'Philadelphia Phoenix':MatchPhl,
            'Raleigh Flyers':MatchRal,
            'Rochester Dragons':MatchRoc,
            'Salt Lake Lions':MatchSLC,
            'San Diego Growlers':MatchSD,
            'San Francisco FlameThrowers':MatchSF,
            'San Jose Spiders':MatchSJ,
            'Seattle Cascades':MatchSeaC,
            'Seattle Raptors':MatchSeaR,
            'Toronto Rush':MatchTor,
            'Tampa Bay Cannons':MatchTB,
            'Vancouver Riptide':MatchVan
}
