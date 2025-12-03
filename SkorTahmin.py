# -*- coding: utf-8 -*-
"""
Live Football Prediction System (Final Polish - Menu Update)
Features: Hybrid Engine, Expert Analysis, Smart Decimal Commentary, Full Localization.

Author: Senior Python Developer
Date: 2025
"""

import requests
import pandas as pd
import numpy as np
import xgboost as xgb
import time
import sys
import warnings
import math
from datetime import datetime

warnings.filterwarnings('ignore')

# CONFIGURATION
API_KEY = "YOUR_KEY_HERE"
API_BASE_URL = "http://api.football-data.org/v4"

COMPETITIONS = [
    ('Premier League (İngiltere)', 'PL'),
    ('Champions League (Avrupa - Uluslararası)', 'CL'),
    ('Bundesliga (Almanya)', 'BL1'),
    ('Serie A (İtalya)', 'SA'),
    ('La Liga (İspanya)', 'PD'),
    ('Ligue 1 (Fransa)', 'FL1'),
    ('Eredivisie (Hollanda)', 'DED'),
    ('Primeira Liga (Portekiz)', 'PPL'),
    ('Championship (İngiltere - 2. Lig)', 'ELC'),
    ('Série A (Brezilya)', 'BSA')
]

# API MANAGER
class FootballDataAPI:
    def __init__(self):
        self.headers = {
            'X-Auth-Token': API_KEY,
            'User-Agent': 'FootballExpert/9.0'
        }

    def _make_request(self, endpoint, params=None):
        url = f"{API_BASE_URL}/{endpoint}"
        time.sleep(1.2) # Rate limit safety
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                print("⚠️ API Hız Sınırı (429). 5sn bekleniyor...")
                time.sleep(5)
                return self._make_request(endpoint, params)
            else:
                print(f"❌ API Hatası ({response.status_code})")
                return None
        except Exception as e:
            print(f"❌ Bağlantı Hatası: {e}")
            return None

    def get_scheduled_matches(self, competition_code):
        print(f"\n🌍 {competition_code} Fikstürü Çekiliyor...")
        endpoint = f"competitions/{competition_code}/matches"
        params = {'status': 'SCHEDULED'}
        data = self._make_request(endpoint, params)
        matches = []
        if data and 'matches' in data:
            sorted_matches = sorted(data['matches'], key=lambda x: x['utcDate'])
            for m in sorted_matches[:10]:
                matches.append({
                    'id': m['id'],
                    'date': m['utcDate'][:10],
                    'home_team': m['homeTeam']['name'],
                    'home_id': m['homeTeam']['id'],
                    'away_team': m['awayTeam']['name'],
                    'away_id': m['awayTeam']['id'],
                    'competition': competition_code
                })
        return matches

    def get_team_history(self, team_id):
        """Fetch last 30 finished matches."""
        endpoint = f"teams/{team_id}/matches"
        params = {'status': 'FINISHED', 'limit': 30}
        data = self._make_request(endpoint, params)
        history = []
        if data and 'matches' in data:
            for m in data['matches']:
                is_home = (m['homeTeam']['id'] == team_id)
                h_score = m['score']['fullTime']['home']
                a_score = m['score']['fullTime']['away']
                
                if h_score is None or a_score is None: continue
                
                # Identify Opponent
                opponent_id = m['awayTeam']['id'] if is_home else m['homeTeam']['id']
                opponent_name = m['awayTeam']['name'] if is_home else m['homeTeam']['name']

                history.append({
                    'date': m['utcDate'][:10],
                    'is_home': is_home,
                    'goals_scored': h_score if is_home else a_score,
                    'goals_conceded': a_score if is_home else h_score,
                    'opponent_id': opponent_id,
                    'opponent_name': opponent_name,
                    'result': 'W' if (h_score > a_score and is_home) or (a_score > h_score and not is_home) 
                              else ('L' if (h_score < a_score and is_home) or (a_score < h_score and not is_home) 
                              else 'D')
                })
        return history

    def get_standings_full(self, competition_code):
        """Fetch TOTAL, HOME, and AWAY standings."""
        endpoint = f"competitions/{competition_code}/standings"
        data = self._make_request(endpoint)
        
        tables = {'TOTAL': {}, 'HOME': {}, 'AWAY': {}}
        
        if data and 'standings' in data:
            for table in data['standings']:
                t_type = table['type']
                if t_type in tables:
                    for row in table['table']:
                        tables[t_type][row['team']['id']] = {
                            'played': row['playedGames'],
                            'goals_for': row['goalsFor'],
                            'goals_against': row['goalsAgainst'],
                            'points': row['points'],
                            'rank': row['position'],
                            'form': row.get('form', '?')
                        }
        return tables

    def get_top_scorers(self, competition_code):
        endpoint = f"competitions/{competition_code}/scorers"
        data = self._make_request(endpoint)
        scorers = []
        if data and 'scorers' in data:
            for item in data['scorers']:
                scorers.append({
                    'name': item['player']['name'],
                    'goals': item['goals'],
                    'team_id': item['team']['id']
                })
        return scorers

# HYBRID PREDICTION ENGINE & EXPERT ANALYSIS
class UltimatePredictor:
    def calculate_weighted_stats(self, history, team_type_filter):
        """
        Soft Data Split: 70% Venue Specific + 30% Overall
        Also returns last match date for fatigue analysis.
        """
        if not history: return None
        
        df = pd.DataFrame(history)
        
        # Overall Stats
        overall_scored = df['goals_scored'].mean()
        overall_conceded = df['goals_conceded'].mean()
        overall_win = len(df[df['result'] == 'W']) / len(df)
        
        # Venue Specific Stats
        if team_type_filter == 'HOME':
            venue_df = df[df['is_home'] == True]
        else:
            venue_df = df[df['is_home'] == False]
            
        if venue_df.empty:
            venue_scored = overall_scored
            venue_conceded = overall_conceded
            venue_win = overall_win
        else:
            venue_scored = venue_df['goals_scored'].mean()
            venue_conceded = venue_df['goals_conceded'].mean()
            venue_win = len(venue_df[venue_df['result'] == 'W']) / len(venue_df)
            
        # Weighted Calculation
        eff_scored = (venue_scored * 0.7) + (overall_scored * 0.3)
        eff_conceded = (venue_conceded * 0.7) + (overall_conceded * 0.3)
        eff_win = (venue_win * 0.7) + (overall_win * 0.3)
        
        last_match_date = datetime.strptime(df.iloc[-1]['date'], "%Y-%m-%d")
        
        raw_form = "-".join(df['result'].tail(5).tolist()[::-1])
        local_form = raw_form.replace('W', 'G').replace('L', 'M').replace('D', 'B')
        
        return {
            'avg_scored': eff_scored,
            'avg_conceded': eff_conceded,
            'win_rate': eff_win,
            'raw_venue_scored': venue_scored, 
            'raw_venue_win': venue_win,       
            'last_match_date': last_match_date,
            'form': local_form
        }

    def analyze_h2h(self, home_history, away_history, home_id, away_id):
        """Find matches between these two teams."""
        encounters = []
        for h_match in home_history:
            if h_match['opponent_id'] == away_id:
                encounters.append(h_match)
        encounters.sort(key=lambda x: x['date'], reverse=True)
        return encounters

    def calculate_poisson_xg(self, tables, home_id, away_id):
        home_table = tables.get('HOME', {})
        away_table = tables.get('AWAY', {})
        
        if not home_table or not away_table: return 1.5, 1.0
            
        total_home_goals = sum(t['goals_for'] for t in home_table.values())
        total_home_games = sum(t['played'] for t in home_table.values())
        league_avg_home = total_home_goals / total_home_games if total_home_games > 0 else 1.5
        
        total_away_goals = sum(t['goals_for'] for t in away_table.values())
        total_away_games = sum(t['played'] for t in away_table.values())
        league_avg_away = total_away_goals / total_away_games if total_away_games > 0 else 1.0
        
        h_stats = home_table.get(home_id)
        a_stats = away_table.get(away_id)
        
        if not h_stats or not a_stats: return 1.5, 1.0
            
        h_att = (h_stats['goals_for'] / h_stats['played']) / league_avg_home if h_stats['played'] > 0 else 1.0
        a_def = (a_stats['goals_against'] / a_stats['played']) / league_avg_home if a_stats['played'] > 0 else 1.0
        a_att = (a_stats['goals_for'] / a_stats['played']) / league_avg_away if a_stats['played'] > 0 else 1.0
        h_def = (h_stats['goals_against'] / h_stats['played']) / league_avg_away if h_stats['played'] > 0 else 1.0
        
        home_xg = h_att * a_def * league_avg_home
        away_xg = a_att * h_def * league_avg_away
        
        return home_xg, away_xg

    def prepare_training_data(self, home_history, away_history):
        data = []
        def add_rows(history, team_type):
            df = pd.DataFrame(history)
            if df.empty: return
            df['roll_scored'] = df['goals_scored'].rolling(window=5, min_periods=1).mean().shift(1)
            df['roll_conceded'] = df['goals_conceded'].rolling(window=5, min_periods=1).mean().shift(1)
            df = df.dropna()
            for _, row in df.iterrows():
                data.append({
                    'team_type': team_type, 
                    'is_home': 1 if row['is_home'] else 0,
                    'roll_scored': row['roll_scored'],
                    'roll_conceded': row['roll_conceded'],
                    'target_goals': row['goals_scored']
                })
        add_rows(home_history, 1)
        add_rows(away_history, 0)
        return pd.DataFrame(data)

    def predict_hybrid(self, home_stats, away_stats, training_df, poisson_home, poisson_away):
        # XGBoost
        if len(training_df) < 10:
            xgb_home, xgb_away = poisson_home, poisson_away
        else:
            X = training_df[['team_type', 'is_home', 'roll_scored', 'roll_conceded']]
            y = training_df['target_goals']
            model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=50, max_depth=3)
            model.fit(X, y)
            h_in = pd.DataFrame([[1, 1, home_stats['avg_scored'], home_stats['avg_conceded']]], 
                                columns=['team_type', 'is_home', 'roll_scored', 'roll_conceded'])
            a_in = pd.DataFrame([[0, 0, away_stats['avg_scored'], away_stats['avg_conceded']]], 
                                columns=['team_type', 'is_home', 'roll_scored', 'roll_conceded'])
            xgb_home = max(0, model.predict(h_in)[0])
            xgb_away = max(0, model.predict(a_in)[0])
            
        # Hybrid Blending
        final_home = (poisson_home * 0.6) + (xgb_home * 0.4)
        final_away = (poisson_away * 0.6) + (xgb_away * 0.4)
        
        # Sanity Check
        adjusted = False
        if home_stats['win_rate'] > 0.70 and away_stats['win_rate'] < 0.40:
            if final_away > final_home + 0.2:
                final_home = (final_home + 2.0) / 2
                final_away = final_away * 0.7
                adjusted = True
                
        return final_home, final_away, xgb_home, xgb_away, adjusted

    def get_smart_commentary(self, score):
        """Generates commentary based on the decimal part of the score."""
        decimal = score - int(score)
        if decimal > 0.75:
            return f"bir sonraki gole çok yakın ({decimal:.2f})"
        elif decimal < 0.25:
            return f"bu skoru korumakta zorlanabilir ({decimal:.2f})"
        else:
            return f"kararsız bir görüntü çiziyor ({decimal:.2f})"

# MAIN APP
def main():
    print("==================================================")
    print("⚽ FUTBOL TAHMİN SİSTEMİ (FINAL POLISH - MENU UPDATE)")
    print("==================================================")
    
    api = FootballDataAPI()
    predictor = UltimatePredictor()
    
    # 1. League Selection
    print("\nLütfen bir lig seçin:")
    for i, (name, code) in enumerate(COMPETITIONS, 1):
        print(f"{i}. {name} ({code})")
        
    while True:
        try:
            sel = input("\nSeçiminiz (Çıkış için 'q'): ")
            if sel.lower() == 'q': return
            idx = int(sel) - 1
            if 0 <= idx < len(COMPETITIONS):
                league_name, league_code = COMPETITIONS[idx]
                break
            print("❌ Geçersiz seçim.")
        except ValueError: pass
            
    # 2. Fetch Matches
    matches = api.get_scheduled_matches(league_code)
    if not matches:
        print(f"\n❌ {league_name} için planlanmış maç bulunamadı.")
        return
        
    print(f"\n📅 {league_name} - GELECEK MAÇLAR:")
    for i, m in enumerate(matches, 1):
        print(f"{i}. {m['home_team']} vs {m['away_team']} ({m['date']})")
        
    # 3. Select Match
    while True:
        try:
            sel = input("\n🔍 Analiz edilecek maç numarası: ")
            if sel.lower() == 'q': return
            idx = int(sel) - 1
            if 0 <= idx < len(matches):
                match = matches[idx]
                break
            print("❌ Geçersiz seçim.")
        except ValueError: pass
            
    print(f"\n🔄 ANALİZ BAŞLIYOR: {match['home_team']} vs {match['away_team']}...")
    
    # 4. Fetch Data
    print("   📊 Veriler Toplanıyor (Geçmiş, Puan Durumu, Golcüler)...")
    home_history = api.get_team_history(match['home_id'])
    away_history = api.get_team_history(match['away_id'])
    tables = api.get_standings_full(league_code)
    top_scorers = api.get_top_scorers(league_code)
    
    if not home_history or not away_history:
        print("❌ Yetersiz veri.")
        return

    # 5. Calculations
    home_stats = predictor.calculate_weighted_stats(home_history, 'HOME')
    away_stats = predictor.calculate_weighted_stats(away_history, 'AWAY')
    
    # Fatigue
    match_date = datetime.strptime(match['date'], "%Y-%m-%d")
    home_rest = (match_date - home_stats['last_match_date']).days
    away_rest = (match_date - away_stats['last_match_date']).days
    
    # H2H
    h2h_matches = predictor.analyze_h2h(home_history, away_history, match['home_id'], match['away_id'])
    
    # Prediction
    print("   🧠 Hibrit Model Çalışıyor (Poisson + XGBoost)...")
    p_home, p_away = predictor.calculate_poisson_xg(tables, match['home_id'], match['away_id'])
    training_df = predictor.prepare_training_data(home_history, away_history)
    f_home, f_away, x_home, x_away, adjusted = predictor.predict_hybrid(
        home_stats, away_stats, training_df, p_home, p_away
    )
    
    # 6. FINAL REPORT
    print("\n" + "="*60)
    print(f"📋 MAÇ ANALİZ RAPORU: {match['home_team']} vs {match['away_team']}")
    print("="*60)
    
    # 1. Standings & Form
    h_std = tables['TOTAL'].get(match['home_id'], {'rank': '-', 'points': '-', 'form': '?'})
    a_std = tables['TOTAL'].get(match['away_id'], {'rank': '-', 'points': '-', 'form': '?'})
    # Localize form in standings if present
    h_form_std = h_std['form'].replace('W', 'G').replace('L', 'M').replace('D', 'B') if h_std['form'] else '?'
    a_form_std = a_std['form'].replace('W', 'G').replace('L', 'M').replace('D', 'B') if a_std['form'] else '?'
    
    print(f"\n🏆 LİG TABLOSU:")
    print(f"   🏠 {match['home_team']}: {h_std['rank']}. Sıra ({h_std['points']} P) | Form: {home_stats['form']}")
    print(f"   ✈️  {match['away_team']}: {a_std['rank']}. Sıra ({a_std['points']} P) | Form: {away_stats['form']}")
    
    # 2. Venue Stats
    print(f"\n🏟️ SAHA PERFORMANSI & İSTATİSTİK:")
    print(f"   🏠 {match['home_team']} (Evinde): {home_stats['raw_venue_scored']:.1f} Gol/Maç | Evinde Kazanma: %{home_stats['raw_venue_win']*100:.0f}")
    print(f"   ✈️  {match['away_team']} (Deplasmanda): {away_stats['raw_venue_scored']:.1f} Gol/Maç | Deplasmanda Kazanma: %{away_stats['raw_venue_win']*100:.0f}")
    
    # 3. Fatigue & Key Players
    print(f"\n💤 YORGUNLUK & KADRO:")
    h_fatigue = "⚠️ YORGUN" if home_rest < 4 else "✅ Dinç"
    a_fatigue = "⚠️ YORGUN" if away_rest < 4 else "✅ Dinç"
    print(f"   🏠 {match['home_team']}: {home_rest} Gün Dinlenme ({h_fatigue})")
    print(f"   ✈️  {match['away_team']}: {away_rest} Gün Dinlenme ({a_fatigue})")
    
    h_scorers = [p for p in top_scorers if p['team_id'] == match['home_id']]
    a_scorers = [p for p in top_scorers if p['team_id'] == match['away_id']]
    if h_scorers or a_scorers:
        print(f"   🌟 Kilit Oyuncular:")
        for p in h_scorers: print(f"      • {p['name']} ({p['goals']} Gol)")
        for p in a_scorers: print(f"      • {p['name']} ({p['goals']} Gol)")
        
    # 4. H2H
    print(f"\n⚔️ ARAMALARINDAKİ MAÇLAR (H2H):")
    if h2h_matches:
        for m in h2h_matches[:3]: # Show last 3
            print(f"   • {m['date']}: {match['home_team']} {m['goals_scored']}-{m['goals_conceded']} {m['opponent_name']}")
    else:
        print("   • Yakın tarihte karşılaşma bulunamadı.")
        
    # 5. AI Detailed Analysis (Smart Decimal)
    print(f"\n🔮 YAPAY ZEKA DETAYLI ANALİZİ:")
    print(f"   ⚽ Skor Beklentisi (xG): {f_home:.2f} - {f_away:.2f}")
    
    h_comm = predictor.get_smart_commentary(f_home)
    a_comm = predictor.get_smart_commentary(f_away)
    
    print(f"   🏠 {match['home_team']}: {int(f_home)} golü bulması bekleniyor ({f_home:.2f})")
    print(f"      👉 ...ve istatistikler {h_comm}")
    print(f"   ✈️  {match['away_team']}: {int(f_away)} golü bulması bekleniyor ({f_away:.2f})")
    print(f"      👉 ...ve istatistikler {a_comm}")
    
    if adjusted:
        print("   ⚠️ (Model istatistiksel verilerle uyumlu hale getirildi)")
        
    # 6. Final Result
    print(f"\n🏁 NİHAİ SONUÇ:")
    print(f"   ⚽ Skor: {round(f_home)} - {round(f_away)}")
    
    diff = f_home - f_away
    if diff > 0.5:
        print(f"   💡 ÖNERİ: {match['home_team']} Kazanır")
    elif diff < -0.5:
        print(f"   💡 ÖNERİ: {match['away_team']} Kazanır")
    else:
        print(f"   💡 ÖNERİ: Beraberlik")
            
    print("="*60)
    sys.stdout.flush()
    time.sleep(1)

if __name__ == "__main__":
    main()
