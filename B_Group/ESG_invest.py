import streamlit as st
import numpy as np
import pandas as pd
import scipy.optimize as sco
import matplotlib.pyplot as plt
import os
os.environ["STREAMLIT_SERVER_PORT"] = "8501"

# Sample stock returns data
np.random.seed(42)
stocks_returns = pd.DataFrame({
    'CDL': np.random.normal(0.1, 0.2, 100),
    'DRAX': np.random.normal(0.08, 0.18, 100),
    'Maxeon': np.random.normal(0.12, 0.22, 100),
    'ST-Eng': np.random.normal(0.09, 0.15, 100),
    'Vena': np.random.normal(0.11, 0.19, 100)
})

# Sample ESG scores (from 0 to 100)
esg_scores = np.array([80, 65, 75, 90, 70])  

# Calculate expected returns and covariance matrix
expected_returns = stocks_returns.mean()
cov_matrix = stocks_returns.cov()

# Portfolio optimization function
def portfolio_optimization(expected_returns, cov_matrix, esg_scores, risk_tolerance, esg_weight, return_weight):
    def objective(weights):
        portfolio_return = np.dot(weights, expected_returns)  # Portfolio expected return
        portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))  # Portfolio risk (variance)
        esg_score = np.dot(weights, esg_scores)  # Weighted ESG score
        # Objective function balances return, risk, and ESG score
        return - (return_weight * portfolio_return + esg_weight * esg_score - risk_tolerance * portfolio_risk)

    # Constraints: sum of weights should be 1, each weight should be between 0 and 1, and max weight per stock should be capped
    constraints = (
        {'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1},  # Sum of weights must be 1
        {'type': 'ineq', 'fun': lambda weights: 0.4 - weights.max()}  # Max weight for any single stock should be less than or equal to 40%
    )
    
    bounds = tuple((0, 1) for asset in range(len(expected_returns)))

    # Initial guess: equally distributed weights, but small adjustments to avoid extreme solutions
    initial_guess = [1.0 / len(expected_returns)] * len(expected_returns)

    # Use minimization function to find optimal solution
    result = sco.minimize(objective, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)
    
    # Ensure the result is valid, otherwise return an equal weight portfolio
    if not result.success:
        st.error("Optimization failed. Using equal weights instead.")
        return np.array([1.0 / len(expected_returns)] * len(expected_returns))
    
    return result.x

# Streamlit user interface
def main():
    st.title("Personalized ESG Portfolio Optimization")

    # User input: Risk tolerance
    risk_tolerance = st.slider("Risk Tolerance", 0.0, 1.0, 0.5)  # 0: Low risk, 1: High risk

    # User input: ESG weight
    esg_weight = st.slider("ESG Weight", 0.0, 1.0, 0.3)  # ESG score weight
    return_weight = 1.0 - esg_weight  # Return weight, the remainder

    # Display portfolio optimization result
    if st.button("Generate Optimized Portfolio"):
        optimal_weights = portfolio_optimization(expected_returns, cov_matrix, esg_scores, risk_tolerance, esg_weight, return_weight)
        
        # Display optimal portfolio weights
        st.subheader("Optimized Portfolio Weights")
        portfolio = pd.DataFrame(optimal_weights, index=stocks_returns.columns, columns=["Weight"])
        st.write(portfolio)

        # Calculate and display portfolio performance
        portfolio_return = np.dot(optimal_weights, expected_returns)
        portfolio_risk = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights)))
        portfolio_esg = np.dot(optimal_weights, esg_scores)

        st.subheader("Portfolio Performance")
        st.write(f"Expected Return: {portfolio_return:.2%}")
        st.write(f"Expected Risk (Standard Deviation): {portfolio_risk:.2%}")
        st.write(f"ESG Score: {portfolio_esg:.2f}")

        # Plot the portfolio weight distribution
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.bar(stocks_returns.columns, optimal_weights, color='teal')
        ax.set_title("Optimized Stock Weights")
        ax.set_xlabel("Stocks")
        ax.set_ylabel("Weight")
        st.pyplot(fig)

if __name__ == "__main__":
    main()




