import pandas as pd
import numpy as np
from scipy.stats import norm
from scipy.stats import beta


def boot_site_cvr(data, threshold=100, n_bootstrap=10):
    
    # Filter impressions based on threshold
    data_boot = data[data['Imps'] >= threshold].copy()

    # Calculate the overall average CVR
    average_cvr = data_boot['Total Conversions'].sum() / data_boot['Imps'].sum()

    # Function to bootstrap CVR for a site
    def bootstrap_cvr(total_conversions, imps, n_bootstrap=10):
        bootstrap_cvrs = []
        for _ in range(n_bootstrap):
            sample_conversions = np.random.binomial(imps, total_conversions / imps)
            sample_cvr = sample_conversions / imps
            bootstrap_cvrs.append(sample_cvr)
        return bootstrap_cvrs

    # Lists to store the results
    high_cvrs = {"Site Domain": [], "Total Conversions": [], "Imps": [], "CVR": []}
    low_cvrs = {"Site Domain": [], "Total Conversions": [], "Imps": [], "CVR": []}

    for index, row in data_boot.iterrows():
        site = row['Site Domain']
        conversions = row['Total Conversions']
        imps = row['Imps']
        site_cvr = row['CVR']

        # Bootstrap CVR for the site
        bootstrap_distribution = bootstrap_cvr(conversions, imps, n_bootstrap=n_bootstrap)
        ci_lower = np.percentile(bootstrap_distribution, 5)  # 2.5 percentile
        ci_upper = np.percentile(bootstrap_distribution, 95) # 97.5 percentile

        # Check if average CVR falls outside this interval and categorize
        if average_cvr < ci_lower or average_cvr > ci_upper:
            if site_cvr > average_cvr:
                high_cvrs["Site Domain"].append(site)
                high_cvrs["Total Conversions"].append(conversions)
                high_cvrs['Imps'].append(imps)
                high_cvrs["CVR"].append(site_cvr)
            else:
                low_cvrs["Site Domain"].append(site)
                low_cvrs["Total Conversions"].append(conversions)
                low_cvrs['Imps'].append(imps)
                low_cvrs["CVR"].append(site_cvr)

    high_cvrs = pd.DataFrame(high_cvrs)
    low_cvrs = pd.DataFrame(low_cvrs)

    return high_cvrs, low_cvrs


def bi_site_cvr(data, threshold=100, confidence_level=0.95):
    
    # Filter data for impression threshold
    data_bi = data[data['Imps'] >= threshold].copy()

    # Calculate the overall average CVR
    average_cvr = data_bi['Total Conversions'].sum() / data_bi['Imps'].sum()

    # Confidence level and corresponding z-score
    z_score = norm.ppf((1 + confidence_level) / 2)

    # Lists to store the results
    high_cvrs = {"Site Domain": [], "Total Conversions": [], "Imps": [], "CVR": []}
    low_cvrs = {"Site Domain": [], "Total Conversions": [], "Imps": [], "CVR": []}

    for index, row in data_bi.iterrows():
        site = row['Site Domain']
        conversions = row['Total Conversions']
        imps = row['Imps']
        site_ctr = row['CVR']  # Assuming CVR is already in proportion

        # Calculate confidence interval for site's CVR
        ci_lower = site_ctr - z_score * np.sqrt(site_ctr * (1 - site_ctr) / imps)
        ci_upper = site_ctr + z_score * np.sqrt(site_ctr * (1 - site_ctr) / imps)

        # Check if average CVR falls outside this interval and categorize
        if average_cvr < ci_lower or average_cvr > ci_upper:
            if site_ctr > average_cvr:
                high_cvrs["Site Domain"].append(site)
                high_cvrs["Total Conversions"].append(conversions)
                high_cvrs['Imps'].append(imps)
                high_cvrs["CVR"].append(site_ctr)
            else:
                low_cvrs["Site Domain"].append(site)
                low_cvrs["Total Conversions"].append(conversions)
                low_cvrs['Imps'].append(imps)
                low_cvrs["CVR"].append(site_ctr)

    high_cvrs = pd.DataFrame(high_cvrs)
    low_cvrs = pd.DataFrame(low_cvrs)

    return high_cvrs, low_cvrs

def bay_site_cvr(data, alpha_prior=1, beta_prior=20, threshold=100):
    
    # Filter data for impression threshold
    data_bay = data[data['Imps'] >= threshold].copy()
    
    # Calculate the overall average CVR
    average_cvr = data_bay['Total Conversions'].sum() / data_bay['Imps'].sum()


    # Dictionaries to store results
    high_cvrs = {"Site Domain": [], "Imps": [], "Total Conversions": [], "CVR": [], "Probability": []}
    low_cvrs = {"Site Domain": [], "Imps": [], "Total Conversions": [], "CVR": [], "Probability": []}

    for index, row in data_bay.iterrows():
        
        site = row['Site Domain']
        conversions = row['Total Conversions']
        imps = row['Imps']
        cvr = row['CVR']

        # Update Beta distribution with observed data
        alpha_posterior = alpha_prior + conversions
        beta_posterior = beta_prior + (imps - conversions)

        # Calculate the probability that the site's CVR is greater than the average CVR
        prob = 1 - beta.cdf(average_cvr, alpha_posterior, beta_posterior)

        # Categorize based on probability
        if prob > 0.50:
            high_cvrs["Site Domain"].append(site)
            high_cvrs["Probability"].append(prob)
            high_cvrs["Imps"].append(imps)
            high_cvrs["CVR"].append(cvr)
            high_cvrs["Total Conversions"].append(conversions)
        else:
            low_cvrs["Site Domain"].append(site)
            low_cvrs["Probability"].append(prob)
            low_cvrs["Imps"].append(imps)
            low_cvrs["CVR"].append(cvr)
            low_cvrs["Total Conversions"].append(conversions)

    high_cvrs = pd.DataFrame(high_cvrs)
    low_cvrs = pd.DataFrame(low_cvrs)
    
    high_cvrs = high_cvrs[high_cvrs["Total Conversions"] != 0]

    return high_cvrs, low_cvrs

