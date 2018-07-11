import re
import sqlite3
import pandas as pd

def clean_column(dirty):
    """Applies some regex to remove the units from the column names"""
    clean = re.sub(r'_*\(*[µmg]+\)*$', '', dirty)
    clean = clean.rstrip('_ ').lower()
    clean = re.sub('[^a-z0-9_]+', '', clean)
    return clean

def build_composition(conn):
    """Transform USDA Excel file into long table, clean, and save to database"""
    df = pd.read_excel('usda_data.xlsx')
    df.columns = [clean_column(c) for c in df.columns]
    df = df.drop([
        'refuse_pct', 'gmwt_2', 'gmwt_desc2', 'gmwt_desc1', 'gmwt_1',
        'panto_acid', 'ash', 'folate_tot', 'folic_acid', 'food_folate',
        'folate_dfe', 'choline_tot', 'retinol', 'alpha_carot', 'beta_carot',
        'beta_crypt', 'lycopene', 'lutzea', 'vit_d_iu', 'vit_a_rae',
        'fa_sat', 'fa_mono', 'fa_poly', 'vit_a_iu'], axis=1)
    df = df.rename(index=str, columns={'ndb_no': 'item_id', 'shrt_desc': 'desc'})
    df['desc'] = df['desc'].str.replace(',', ', ').str.lower()
    df = pd.melt(df, id_vars=['item_id', 'desc'])
    df = df.rename(index=str, columns={'variable': 'component'})
    df.to_sql('composition', conn, if_exists='replace')

def build_units(conn):
    """Create mapping table from columns to units of measurement"""
    units = {
        'water': 'g', 'protein': 'g', 'lipid_tot': 'g',
        'carbohydrt': 'g', 'fiber_td': 'g', 'sugar_tot': 'g',
        'calcium': 'mg', 'iron': 'mg', 'magnesium': 'mg',
        'phosphorus': 'mg', 'potassium': 'mg', 'sodium': 'mg',
        'zinc': 'mg', 'copper': 'mg', 'manganese': 'mg',
        'selenium': 'ug', 'vit_c': 'mg', 'thiamin': 'mg',
        'riboflavin': 'mg', 'niacin': 'mg', 'vit_b6': 'mg',
        'vit_b12': 'ug', 'vit_e': 'mg', 'vit_d': 'ug',
        'vit_k': 'ug', 'cholestrl': 'mg'}
    units_df = pd.DataFrame(units, index=['unit']).T
    units_df.index.name = 'component'
    units_df.to_sql('units', conn, if_exists='replace')

def build_conversion(conn):
    """Create mapping table with decimal conversion factors for each unit"""
    conversion =  pd.DataFrame({'g': 1, 'mg': 1e-3, 'ug': 1e-6}, index=['conversion']).T
    conversion.index.name = 'unit'
    conversion.to_sql('conversion', conn, if_exists='replace')

if __name__ == '__main__':
    print('Creating SQLite database...')
    conn = sqlite3.connect('usda.db')
    print('Building composition table...')
    build_composition(conn)
    print('Building units table...')
    build_units(conn)
    print('Building conversion table...')
    build_conversion(conn)
    print('Done! Database created successfully.')
