import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import norm, beta
from helper import boot_site, bi_site, bay_site


def main():
    
    st.title("Site Domain Analysis App")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    if uploaded_file is not None:
        
        data = pd.read_csv(uploaded_file)

        dsp = st.selectbox("Which dsp is this report from?", ["Xandr", "DV360", "TTD", "Yahoo"])

        if dsp != "Xandr":
            imp_bool = "Impressions" in data.columns
            if imp_bool:
                data["Imps"] = data["Impressions"]
            else:
                st.write("No impression column")
        else:
            imp_bool = "Imps" in data.columns
            if not imp_bool:
                st.write("No impression column")

        clicks_bool = "Clicks" in data.columns
        if not clicks_bool:
            st.write("No click column")

        if imp_bool and clicks_bool:
            ctr_bool = "CTR %" in data.columns
            if not ctr_bool:
                ctr_bool_two = "CTR" in data.columns
                if ctr_bool_two:
                    data["CTR %"] = data["CTR"]
                else:
                    try:
                        data["CTR %"] = data.Clicks / data.Imps
                    except:
                        st.write("Not possible to calcuate CTR")


        method = st.selectbox("Choose the analysis method", 
                              ["Bootstrapping", "Binomial", "Bayesian"])
        
        threshold = st.number_input("Enter impression threshold", 
                                          min_value=0, value=100, step=1, format="%d")

        # Method-specific parameters
        if method == "Bootstrapping":
            n_bootstrap = st.number_input("Enter number of times to bootstrap (default is 10)", 
                                          min_value=10, value=10, step=1, format="%d")
        elif method == "Binomial":
            confidence_level = st.number_input("Enter confidence level (e.g., 0.95 for 95%)",
                                               min_value=0.0, max_value=1.0, value=0.95, step=0.05, format="%f")
        elif method == "Bayesian":
            alpha_prior = st.number_input("Enter alpha prior", min_value=1, value=1, step=1)
            beta_prior = st.number_input("Enter beta prior", min_value=1, value=20, step=1)

        if st.button('Analyze'):
            if method == "Bootstrapping":
                high_ctrs, low_ctrs = boot_site(data, threshold=threshold, n_bootstrap=n_bootstrap)
                st.write("High CTR Sites")
                st.dataframe(high_ctrs)
                st.write("Low CTR Sites")
                st.dataframe(low_ctrs)

            elif method == "Binomial":
                high_ctrs, low_ctrs = bi_site(data, threshold=threshold, confidence_level=confidence_level)
                st.write("High CTR Sites")
                st.dataframe(high_ctrs)
                st.write("Low CTR Sites")
                st.dataframe(low_ctrs)

            elif method == "Bayesian":
                high_ctrs, low_ctrs = bay_site(data, threshold=threshold, alpha_prior=alpha_prior, beta_prior=beta_prior)
                st.write("High CTR Sites")
                st.dataframe(high_ctrs)
                st.write("Low CTR Sites")
                st.dataframe(low_ctrs)

if __name__ == "__main__":
    main()

