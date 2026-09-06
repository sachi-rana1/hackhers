import pandas as pd

def clean_scraped_fares(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans raw pricing anomalies using targeted Interquartile Range (IQR) 
    calculations performed inside distinct route & lead-time groups.
    """
    cleaned_frames = []
    
    # We must calculate distinct bounds to avoid dropping cheap T+45 flights as outliers
    for (route, lead_time), group in df_raw.groupby(['route', 'lead_time']):
        q1 = group['total_fare'].quantile(0.25)
        q3 = group['total_fare'].quantile(0.75)
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        filtered = group[(group['total_fare'] >= lower_bound) & (group['total_fare'] <= upper_bound)]
        cleaned_frames.append(filtered)
        
    if not cleaned_frames:
        return df_raw
    return pd.concat(cleaned_frames).reset_index(drop=True)
