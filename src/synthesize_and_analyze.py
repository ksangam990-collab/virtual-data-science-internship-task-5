"""
Week 5: Comprehensive Data Science Capstone & Strategic Decision Intelligence
Candidate 1: ksangam990
Domain: Enterprise Customer Retention & Telecommunications Revenue Intelligence
Author: ksangam990
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, roc_curve, precision_recall_curve, auc
)

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 150

BASE_DIR = r"C:\Users\USER\Downloads\websites\capstone-strategic-report-ksangam990"
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

def main():
    print("[1/6] Loading Telco Customer Churn Dataset for Capstone Synthesis...")
    csv_file = os.path.join(DATA_DIR, "telco_churn.csv")
    df = pd.read_csv(csv_file)
    print(f"Loaded raw dataset with dimensions: {df.shape}")

    # Cleaning: Handle TotalCharges blanks
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'].astype(str).str.strip(), errors='coerce').fillna(0.0)
    df['SeniorCitizen'] = df['SeniorCitizen'].astype(str)
    
    # Financial metrics
    total_customers = len(df)
    churn_count = (df['Churn'] == 'Yes').sum()
    churn_rate = churn_count / total_customers
    total_monthly_revenue = df['MonthlyCharges'].sum()
    churned_monthly_revenue = df[df['Churn'] == 'Yes']['MonthlyCharges'].sum()
    annual_churn_revenue_loss = churned_monthly_revenue * 12

    print(f"Total Cohort: {total_customers:,} | Churned: {churn_count:,} ({churn_rate*100:.2f}%)")
    print(f"Monthly Revenue at Risk: ${churned_monthly_revenue:,.2f} | Annualized Loss: ${annual_churn_revenue_loss:,.2f}")

    # Figure 1: Churn Breakdown by Contract and Payment Method
    print("[2/6] Generating Figure 1: Financial & Structural Churn Distribution...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    
    # Contract Churn Rate
    contract_churn = df.groupby('Contract')['Churn'].apply(lambda x: (x == 'Yes').mean() * 100).reset_index()
    contract_order = ['Month-to-month', 'One year', 'Two year']
    contract_churn = contract_churn.set_index('Contract').reindex(contract_order).reset_index()
    
    colors_contract = ['#e6550d', '#fdae6b', '#31a354']
    bars1 = ax1.bar(contract_churn['Contract'], contract_churn['Churn'], color=colors_contract, edgecolor='black', width=0.55)
    ax1.set_title("A. Churn Propensity by Contract Type (%)", fontsize=11, fontweight='bold', pad=10)
    ax1.set_ylabel("Churn Percentage (%)", fontsize=10, fontweight='bold')
    ax1.set_ylim(0, 50)
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, yval + 1.2, f"{yval:.1f}%", ha='center', va='bottom', fontsize=10, fontweight='bold')

    # Payment Method Churn Rate
    pm_churn = df.groupby('PaymentMethod')['Churn'].apply(lambda x: (x == 'Yes').mean() * 100).sort_values(ascending=False).reset_index()
    bars2 = ax2.barh(pm_churn['PaymentMethod'], pm_churn['Churn'], color='#3182bd', edgecolor='navy', height=0.55)
    ax2.set_title("B. Churn Propensity by Payment Channel (%)", fontsize=11, fontweight='bold', pad=10)
    ax2.set_xlabel("Churn Percentage (%)", fontsize=10, fontweight='bold')
    ax2.set_xlim(0, 55)
    for bar in bars2:
        xval = bar.get_width()
        ax2.text(xval + 1.0, bar.get_y() + bar.get_height()/2, f"{xval:.1f}%", ha='left', va='center', fontsize=9.5, fontweight='bold')

    plt.suptitle("Figure 1: Structural Drivers of Customer Attrition Across Contract and Payment Channels", fontsize=12, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig1_path = os.path.join(FIGURES_DIR, "fig1_churn_driver_waterfall.png")
    plt.savefig(fig1_path, dpi=160, bbox_inches='tight')
    plt.close()
    print(f"Generated Figure 1: {fig1_path}")

    # Figure 2: Tenure vs Churn Probability
    print("[3/6] Generating Figure 2: Tenure Decay Curves by Contract Architecture...")
    plt.figure(figsize=(9, 5.2))
    tenure_bins = np.arange(0, 75, 6)
    df['Tenure_Bin'] = pd.cut(df['tenure'], bins=tenure_bins)
    
    for c_type, col in zip(['Month-to-month', 'One year', 'Two year'], ['#de2d26', '#3182bd', '#31a354']):
        sub = df[df['Contract'] == c_type]
        curve = sub.groupby('Tenure_Bin')['Churn'].apply(lambda x: (x == 'Yes').mean()).dropna()
        bin_mids = [b.mid for b in curve.index]
        plt.plot(bin_mids, curve.values * 100, marker='o', lw=2.4, color=col, label=f"Contract: {c_type}")

    plt.title("Figure 2: Empirical Churn Decay Trajectory Across Customer Tenure Lifecycle", fontsize=12, fontweight='bold', pad=12)
    plt.xlabel("Account Tenure (Months in Service)", fontsize=11, fontweight='bold')
    plt.ylabel("Observed Churn Rate (%)", fontsize=11, fontweight='bold')
    plt.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=10)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    fig2_path = os.path.join(FIGURES_DIR, "fig2_contract_tenure_risk.png")
    plt.savefig(fig2_path, dpi=160)
    plt.close()
    print(f"Generated Figure 2: {fig2_path}")

    # Prepare ML dataset
    print("[4/6] Preprocessing Features & Training Machine Learning Models...")
    y = (df['Churn'] == 'Yes').astype(int).values
    feature_df = df.drop(columns=['customerID', 'Churn', 'Tenure_Bin'])
    
    # One-hot encode categoricals
    cat_cols = feature_df.select_dtypes(include=['object']).columns.tolist()
    num_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']
    
    X_encoded = pd.get_dummies(feature_df, columns=cat_cols, drop_first=True)
    feature_names = X_encoded.columns.tolist()

    X_train, X_test, y_train, y_test = train_test_split(
        X_encoded, y, test_size=0.20, random_state=42, stratify=y
    )

    models = {
        "Logistic Regression": Pipeline([
            ('scaler', StandardScaler()),
            ('model', LogisticRegression(max_iter=1000, C=1.0, random_state=42))
        ]),
        "Random Forest": Pipeline([
            ('scaler', StandardScaler()),
            ('model', RandomForestClassifier(n_estimators=100, max_depth=8, min_samples_leaf=4, random_state=42))
        ]),
        "Gradient Boosting": Pipeline([
            ('scaler', StandardScaler()),
            ('model', GradientBoostingClassifier(n_estimators=100, learning_rate=0.08, max_depth=4, random_state=42))
        ])
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    results = {}
    test_probs = {}

    for name, pipe in models.items():
        cv_scores = cross_val_score(pipe, X_train, y_train, cv=cv, scoring='accuracy')
        cv_roc = cross_val_score(pipe, X_train, y_train, cv=cv, scoring='roc_auc')

        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        y_prob = pipe.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_prob)
        cm = confusion_matrix(y_test, y_pred)

        results[name] = {
            "cv_accuracy_mean": float(np.mean(cv_scores)),
            "cv_accuracy_std": float(np.std(cv_scores)),
            "cv_roc_mean": float(np.mean(cv_roc)),
            "cv_roc_std": float(np.std(cv_roc)),
            "test_accuracy": float(acc),
            "test_precision": float(prec),
            "test_recall": float(rec),
            "test_f1": float(f1),
            "test_roc_auc": float(roc_auc),
            "confusion_matrix": cm.tolist()
        }
        test_probs[name] = y_prob
        print(f" -> {name}: Test Acc={acc*100:.2f}%, Recall={rec*100:.2f}%, F1={f1:.4f}, ROC-AUC={roc_auc:.4f}")

    # Figure 3: ROC and Precision-Recall Curves
    print("[5/6] Generating Figure 3: Dual ROC & Precision-Recall Diagnostic Curves...")
    fig, (ax_roc, ax_pr) = plt.subplots(1, 2, figsize=(14, 5.5))
    colors_m = ['#1f77b4', '#2ca02c', '#d62728']

    for (name, y_prob), col in zip(test_probs.items(), colors_m):
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        r_val = auc(fpr, tpr)
        ax_roc.plot(fpr, tpr, color=col, lw=2.2, label=f"{name} (AUC = {r_val:.4f})")

        precision_vals, recall_vals, _ = precision_recall_curve(y_test, y_prob)
        pr_val = auc(recall_vals, precision_vals)
        ax_pr.plot(recall_vals, precision_vals, color=col, lw=2.2, label=f"{name} (PR-AUC = {pr_val:.4f})")

    ax_roc.plot([0, 1], [0, 1], color='#7f7f7f', linestyle='--', lw=1.5, label='Chance (0.50)')
    ax_roc.set_title("A. Receiver Operating Characteristic (ROC)", fontsize=11, fontweight='bold', pad=10)
    ax_roc.set_xlabel("False Positive Rate (1 - Specificity)", fontsize=10, fontweight='bold')
    ax_roc.set_ylabel("True Positive Rate (Sensitivity)", fontsize=10, fontweight='bold')
    ax_roc.legend(loc="lower right", frameon=True)

    base_prev = np.mean(y_test)
    ax_pr.plot([0, 1], [base_prev, base_prev], color='#7f7f7f', linestyle='--', lw=1.5, label=f'Prevalence ({base_prev:.2f})')
    ax_pr.set_title("B. Precision-Recall Curves", fontsize=11, fontweight='bold', pad=10)
    ax_pr.set_xlabel("Recall (Sensitivity)", fontsize=10, fontweight='bold')
    ax_pr.set_ylabel("Precision (Positive Predictive Value)", fontsize=10, fontweight='bold')
    ax_pr.legend(loc="lower left", frameon=True)

    plt.suptitle("Figure 3: Multi-Model Discriminative Benchmark on Customer Churn Holdout Set (n=1,409)", fontsize=12, fontweight='bold', y=1.02)
    plt.tight_layout()
    fig3_path = os.path.join(FIGURES_DIR, "fig3_model_roc_pr_comparison.png")
    plt.savefig(fig3_path, dpi=160, bbox_inches='tight')
    plt.close()
    print(f"Generated Figure 3: {fig3_path}")

    # Figure 4: Feature Importance Drivers
    print("[6/6] Generating Figure 4 & Figure 5 (Feature Importance & Strategic Matrix)...")
    gb_model = models["Gradient Boosting"].named_steps['model']
    imp = gb_model.feature_importances_
    indices = np.argsort(imp)[::-1][:10]
    top_f = [feature_names[i] for i in indices]
    top_v = imp[indices]

    plt.figure(figsize=(9, 5.2))
    bars = plt.barh(range(len(top_f)), top_v[::-1], color='#1d4e89', edgecolor='black', alpha=0.85)
    clean_f_names = [f.replace('Contract_', 'Contract: ').replace('PaymentMethod_', 'Payment: ').replace('InternetService_', 'Internet: ') for f in top_f[::-1]]
    plt.yticks(range(len(top_f)), clean_f_names, fontsize=9.5)
    plt.xlabel('Gradient Boosting Relative Feature Importance (Gini)', fontsize=10.5, fontweight='bold')
    plt.title('Figure 4: Top 10 Quantitative Churn Predictors (Gradient Boosting Ensemble)', fontsize=12, fontweight='bold', pad=12)
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 0.005, bar.get_y() + bar.get_height()/2, f"{width:.3f}", va='center', ha='left', fontsize=9, fontweight='bold')
    plt.xlim(0, max(top_v) * 1.18)
    plt.tight_layout()
    fig4_path = os.path.join(FIGURES_DIR, "fig4_feature_importance_drivers.png")
    plt.savefig(fig4_path, dpi=160)
    plt.close()
    print(f"Generated Figure 4: {fig4_path}")

    # Figure 5: Strategic Retention Matrix (Risk vs CLV)
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 4 Quadrants
    ax.axvline(0.5, color='#4a5568', linestyle='--', lw=1.5)
    ax.axhline(0.5, color='#4a5568', linestyle='--', lw=1.5)
    
    # Fill colors
    ax.fill_between([0, 0.5], 0.5, 1, color='#e6fffa', alpha=0.6) # Low Risk, High CLV (Loyal Advocates)
    ax.fill_between([0.5, 1], 0.5, 1, color='#fff5f5', alpha=0.6) # High Risk, High CLV (Priority Retention)
    ax.fill_between([0, 0.5], 0, 0.5, color='#edf2f7', alpha=0.6) # Low Risk, Low CLV (Maintain & Automate)
    ax.fill_between([0.5, 1], 0, 0.5, color='#fffaf0', alpha=0.6) # High Risk, Low CLV (Targeted Digital Nudge)

    ax.text(0.25, 0.75, "QUADRANT I: PRIME ADVOCATES\n(Low Churn Risk / High Lifetime Value)\n• Cross-sell 5G & bundled streaming\n• VIP loyalty rewards & proactive check-ins\n• Annual contract lock-in incentives",
            ha='center', va='center', fontsize=9.5, fontweight='bold', color='#234e52',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='#319795', alpha=0.9))

    ax.text(0.75, 0.75, "QUADRANT II: CRISIS INTERVENTION 🚨\n(High Churn Risk / High Lifetime Value)\n• Direct executive outreach within 24 hrs\n• Fiber service audit & tech dispatch\n• 20% billing rebate on 1-yr renewal contract",
            ha='center', va='center', fontsize=9.5, fontweight='bold', color='#742a2a',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='#e53e3e', alpha=0.9))

    ax.text(0.25, 0.25, "QUADRANT III: SUSTAIN & AUTOMATE\n(Low Churn Risk / Low Lifetime Value)\n• Automated digital touchpoints\n• Self-service billing optimization\n• Standard retention maintenance",
            ha='center', va='center', fontsize=9.5, fontweight='bold', color='#4a5568',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='#718096', alpha=0.9))

    ax.text(0.75, 0.25, "QUADRANT IV: AUTOMATED DEFENSE\n(High Churn Risk / Low Lifetime Value)\n• Targeted app push notifications\n• Auto-pay discount switches ($5/mo credit)\n• Contract extension micro-promotions",
            ha='center', va='center', fontsize=9.5, fontweight='bold', color='#7b341e',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='#dd6b20', alpha=0.9))

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Predicted Model Churn Probability (Risk Score)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Customer Lifetime Value / Monthly Bill (Normalized)", fontsize=11, fontweight='bold')
    ax.set_title("Figure 5: Enterprise Customer Churn Strategic Decision Matrix\nMapping Machine Learning Risk Scores to Executive Action Levers", fontsize=12, fontweight='bold', pad=12)
    plt.tight_layout()
    fig5_path = os.path.join(FIGURES_DIR, "fig5_strategic_retention_matrix.png")
    plt.savefig(fig5_path, dpi=160)
    plt.close()
    print(f"Generated Figure 5: {fig5_path}")

    # Export metrics JSON
    metrics_export = {
        "cohort_stats": {
            "total_customers": total_customers,
            "churn_count": int(churn_count),
            "churn_rate": float(churn_rate),
            "monthly_churn_loss": float(churned_monthly_revenue),
            "annual_churn_loss": float(annual_churn_revenue_loss)
        },
        "model_results": results
    }
    with open(os.path.join(DATA_DIR, "capstone_metrics.json"), "w") as f:
        json.dump(metrics_export, f, indent=4)
    print("Candidate 1 Capstone data analysis and visualizations complete!")

if __name__ == "__main__":
    main()
