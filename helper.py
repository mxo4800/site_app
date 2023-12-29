import pandas as pd
import numpy as np
from scipy.stats import norm
from scipy.stats import beta


def boot_site(data, threshold=100, n_bootstrap=10):
    
    # Filter impressions based on threshold
    data_boot = data[data['Imps'] >= threshold].copy()

    # Calculate the overall average CTR
    average_ctr = data_boot['Clicks'].sum() / data_boot['Imps'].sum()

    # Function to bootstrap CTR for a site
    def bootstrap_ctr(clicks, imps, n_bootstrap=10):
        bootstrap_ctrs = []
        for _ in range(n_bootstrap):
            sample_clicks = np.random.binomial(imps, clicks / imps)
            sample_ctr = sample_clicks / imps
            bootstrap_ctrs.append(sample_ctr)
        return bootstrap_ctrs

    # Lists to store the results
    high_ctrs = {"Site Domain": [], "Clicks": [], "Imps": [], "CTR": []}
    low_ctrs = {"Site Domain": [], "Clicks": [], "Imps": [], "CTR": []}

    for index, row in data_boot.iterrows():
        site = row['Site Domain']
        clicks = row['Clicks']
        imps = row['Imps']
        site_ctr = row['CTR %']

        # Bootstrap CTR for the site
        bootstrap_distribution = bootstrap_ctr(clicks, imps, n_bootstrap=n_bootstrap)
        ci_lower = np.percentile(bootstrap_distribution, 5)  # 2.5 percentile
        ci_upper = np.percentile(bootstrap_distribution, 95) # 97.5 percentile

        # Check if average CTR falls outside this interval and categorize
        if average_ctr < ci_lower or average_ctr > ci_upper:
            if site_ctr > average_ctr:
                high_ctrs["Site Domain"].append(site)
                high_ctrs["Clicks"].append(clicks)
                high_ctrs['Imps'].append(imps)
                high_ctrs["CTR"].append(site_ctr)
            else:
                low_ctrs["Site Domain"].append(site)
                low_ctrs["Clicks"].append(clicks)
                low_ctrs['Imps'].append(imps)
                low_ctrs["CTR"].append(site_ctr)

    high_ctrs = pd.DataFrame(high_ctrs)
    low_ctrs = pd.DataFrame(low_ctrs)

    return high_ctrs, low_ctrs


def bi_site(data, threshold=100, confidence_level=0.95):
    
    # Filter data for impression threshold
    data_bi = data[data['Imps'] >= threshold].copy()

    # Calculate the overall average CTR
    average_ctr = data_bi['Clicks'].sum() / data_bi['Imps'].sum()

    # Confidence level and corresponding z-score
    z_score = norm.ppf((1 + confidence_level) / 2)

    # Lists to store the results
    high_ctrs = {"Site Domain": [], "Clicks": [], "Imps": [], "CTR": []}
    low_ctrs = {"Site Domain": [], "Clicks": [], "Imps": [], "CTR": []}

    for index, row in data_bi.iterrows():
        site = row['Site Domain']
        clicks = row['Clicks']
        imps = row['Imps']
        site_ctr = row['CTR %']  # Assuming CTR is already in proportion

        # Calculate confidence interval for site's CTR
        ci_lower = site_ctr - z_score * np.sqrt(site_ctr * (1 - site_ctr) / imps)
        ci_upper = site_ctr + z_score * np.sqrt(site_ctr * (1 - site_ctr) / imps)

        # Check if average CTR falls outside this interval and categorize
        if average_ctr < ci_lower or average_ctr > ci_upper:
            if site_ctr > average_ctr:
                high_ctrs["Site Domain"].append(site)
                high_ctrs["Clicks"].append(clicks)
                high_ctrs['Imps'].append(imps)
                high_ctrs["CTR"].append(site_ctr)
            else:
                low_ctrs["Site Domain"].append(site)
                low_ctrs["Clicks"].append(clicks)
                low_ctrs['Imps'].append(imps)
                low_ctrs["CTR"].append(site_ctr)

    high_ctrs = pd.DataFrame(high_ctrs)
    low_ctrs = pd.DataFrame(low_ctrs)

    return high_ctrs, low_ctrs

def bay_site(data, alpha_prior=1, beta_prior=20, threshold=100):
    
    # Filter data for impression threshold
    data_bay = data[data['Imps'] >= threshold].copy()
    
    # Calculate the overall average CTR
    average_ctr = data_bay['Clicks'].sum() / data_bay['Imps'].sum()


    # Dictionaries to store results
    high_ctrs = {"Site Domain": [], "Imps": [], "Clicks": [], "CTR": [], "Probability": []}
    low_ctrs = {"Site Domain": [], "Imps": [], "Clicks": [], "CTR": [], "Probability": []}

    for index, row in data_bay.iterrows():
        
        site = row['Site Domain']
        clicks = row['Clicks']
        imps = row['Imps']
        ctr = row['CTR %']

        # Update Beta distribution with observed data
        alpha_posterior = alpha_prior + clicks
        beta_posterior = beta_prior + (imps - clicks)

        # Calculate the probability that the site's CTR is greater than the average CTR
        prob = 1 - beta.cdf(average_ctr, alpha_posterior, beta_posterior)

        # Categorize based on probability
        if prob > 0.50:
            high_ctrs["Site Domain"].append(site)
            high_ctrs["Probability"].append(prob)
            high_ctrs["Imps"].append(imps)
            high_ctrs["CTR"].append(ctr)
            high_ctrs["Clicks"].append(clicks)
        else:
            low_ctrs["Site Domain"].append(site)
            low_ctrs["Probability"].append(prob)
            low_ctrs["Imps"].append(imps)
            low_ctrs["CTR"].append(ctr)
            low_ctrs["Clicks"].append(clicks)

    high_ctrs = pd.DataFrame(high_ctrs)
    low_ctrs = pd.DataFrame(low_ctrs)
    
    high_ctrs = high_ctrs[high_ctrs.Clicks != 0]

    return high_ctrs, low_ctrs

