import React, { useState, useEffect, useRef } from 'react';

// ─── Types ─────────────────────────────────────────────────────────────────
type Status = 'pending' | 'running' | 'completed';
type Priority = 'critical' | 'high' | 'medium';

interface Step { name: string; owner: string; output: string; priority: Priority; }
interface SubCategory { id: string; name: string; icon: string; steps: Step[]; }
interface Industry {
  id: string; name: string; icon: string;
  color: string; bg: string; description: string;
  subCategories: SubCategory[];
}
interface LogEntry { id: number; time: string; tag: string; text: string; }

// ─── Palette (light, cool, no reds) ────────────────────────────────────────
const C = {
  pageBg: 'linear-gradient(135deg,#f0f4ff 0%,#faf5ff 50%,#f0fdf9 100%)',
  surface: '#ffffff',
  surfaceAlt: '#f8f9ff',
  border: '#e2e8f0',
  text: '#1e1b4b',
  textMid: '#4b5563',
  textLight: '#9ca3af',
  blue: '#4361ee',
  blueLight: '#eef2ff',
  violet: '#7c3aed',
  violetLight: '#f5f3ff',
  teal: '#0d9488',
  tealLight: '#f0fdfa',
  amber: '#d97706',
  amberLight: '#fffbeb',
  sky: '#0284c7',
  skyLight: '#e0f2fe',
  cyan: '#0891b2',
  cyanLight: '#ecfeff',
  emerald: '#059669',
  emeraldLight: '#ecfdf5',
  indigo: '#4f46e5',
  indigoLight: '#eef2ff',
  completedBg: 'rgba(5,150,105,0.09)',
  completedBorder: 'rgba(5,150,105,0.35)',
  completedText: '#065f46',
  runningBg: 'rgba(2,132,199,0.1)',
  runningBorder: 'rgba(2,132,199,0.4)',
  runningText: '#0369a1',
  pendingBg: '#f8f9ff',
  pendingBorder: '#e2e8f0',
  pendingText: '#6b7280',
  critBg: 'rgba(124,58,237,0.09)',
  critBorder: 'rgba(124,58,237,0.3)',
  critText: '#5b21b6',
  highBg: 'rgba(217,119,6,0.09)',
  highBorder: 'rgba(217,119,6,0.3)',
  highText: '#92400e',
  medBg: 'rgba(8,145,178,0.09)',
  medBorder: 'rgba(8,145,178,0.3)',
  medText: '#164e63',
};

// ─── Industries Data ────────────────────────────────────────────────────────
const INDUSTRIES: Industry[] = [
  // ── BANKING & FINANCE ──────────────────────────────────────────────────────
  {
    id: 'banking', name: 'Banking & Finance', icon: '🏦',
    color: '#4361ee', bg: '#eef2ff',
    description: 'End-to-end financial close, MD&A and compliance automation for banks.',
    subCategories: [
      { id: 'retail-banking', name: 'Retail Banking', icon: '👤', steps: [
        { name: '7-Day Financial Close — Pre-close Readiness & Interface Health', owner: 'R2R / GL Operations', output: 'Close Readiness Pack', priority: 'critical' },
        { name: 'Daily GL Reconciliation & Exception Flagging', owner: 'GL Operations', output: 'Reconciliation Report', priority: 'critical' },
        { name: 'Customer Deposit & Loan Portfolio Snapshot', owner: 'Retail Finance', output: 'Portfolio Dashboard', priority: 'high' },
        { name: 'NIM (Net Interest Margin) Variance Analysis', owner: 'FP&A', output: 'NIM Report', priority: 'high' },
        { name: 'Branch P&L Attribution by Region', owner: 'Business Finance', output: 'Branch P&L Pack', priority: 'medium' },
        { name: 'IFRS 9 Credit Loss Provision Calculation (ECL)', owner: 'Credit Risk', output: 'ECL Workbook', priority: 'critical' },
        { name: 'Delinquency & Charge-Off Tracking', owner: 'Collections Finance', output: 'Delinquency Report', priority: 'high' },
        { name: 'Mortgage Pipeline & Origination Report', owner: 'Home Financing', output: 'Pipeline Tracker', priority: 'high' },
        { name: 'Fee Income & Non-Interest Revenue Summary', owner: 'Retail Finance', output: 'Fee Report', priority: 'medium' },
        { name: 'ATM & Digital Channel Cost Allocation', owner: 'Technology Finance', output: 'Cost Allocation Model', priority: 'medium' },
        { name: 'Customer Profitability Segmentation (CPS)', owner: 'Segment Finance', output: 'CPS Model', priority: 'medium' },
        { name: 'Month-End Close Pack & CFO Narrative', owner: 'Controller / CFO Office', output: 'Close Pack', priority: 'critical' },
      ]},
      { id: 'wealth', name: 'Wealth Management', icon: '💎', steps: [
        { name: 'AUM Reconciliation & Daily NAV Validation', owner: 'Fund Operations', output: 'AUM Report', priority: 'critical' },
        { name: 'Fee Revenue Accrual (AUM-Based & Fixed)', owner: 'Revenue Finance', output: 'Fee Accrual Schedule', priority: 'high' },
        { name: 'Portfolio Performance vs Benchmark Attribution', owner: 'Investment Finance', output: 'Performance Report', priority: 'high' },
        { name: 'Client Tier Segmentation & Revenue Ranking', owner: 'Wealth Finance', output: 'Client Analytics', priority: 'medium' },
        { name: 'Advisor Productivity & Revenue Dashboard', owner: 'Sales Finance', output: 'Advisor Scorecard', priority: 'medium' },
        { name: 'Tax Lot & Capital Gains Reporting', owner: 'Tax Operations', output: 'Tax Report', priority: 'high' },
        { name: 'Discretionary vs Advisory Mix Analysis', owner: 'Strategy Finance', output: 'Book Analysis', priority: 'medium' },
        { name: 'Alternative Investments Valuation Memo', owner: 'Valuation Team', output: 'Alt Inv Memo', priority: 'high' },
        { name: 'Regulatory Capital Allocation by Book', owner: 'Risk & Compliance', output: 'Capital Report', priority: 'critical' },
        { name: 'Client Attrition & Retention Metrics', owner: 'CRM Finance', output: 'Retention Dashboard', priority: 'medium' },
        { name: 'Wealth Board Pack & Investor Deck', owner: 'CFO Office', output: 'Board Pack', priority: 'critical' },
      ]},
      { id: 'capital-markets', name: 'Capital Markets', icon: '📈', steps: [
        { name: 'Daily Trading P&L Attribution by Desk', owner: 'Front Office Finance', output: 'Daily P&L Flash', priority: 'critical' },
        { name: 'Mark-to-Market Positions & Fair Value Adjustment', owner: 'Valuation Control', output: 'MTM Report', priority: 'critical' },
        { name: 'VaR / CVaR Limit Utilisation Report', owner: 'Market Risk', output: 'Risk Limits Dashboard', priority: 'critical' },
        { name: 'Repo & Securities Financing Summary', owner: 'Treasury', output: 'SFT Report', priority: 'high' },
        { name: 'Derivatives Margining & Collateral Report', owner: 'Collateral Management', output: 'Margin Report', priority: 'high' },
        { name: 'FRTB IMA / SA Capital Calculation', owner: 'Market Risk Capital', output: 'FRTB Pack', priority: 'critical' },
        { name: 'Revenue by Product Hierarchy (Rates/FX/Credit)', owner: 'Product Control', output: 'Revenue Tree', priority: 'high' },
        { name: 'Counterparty Credit Exposure (CVA / XVA)', owner: 'Credit Risk', output: 'CVA Report', priority: 'high' },
        { name: 'Trade Reconciliation & Break Resolution', owner: 'Middle Office', output: 'Break Report', priority: 'medium' },
        { name: 'Investor Relations Metrics & Deal Pipeline', owner: 'DCM / ECM Finance', output: 'IR Pack', priority: 'medium' },
        { name: 'Month-End Capital Markets Close Pack', owner: 'Finance Controller', output: 'CM Close Pack', priority: 'critical' },
      ]},
      { id: 'risk-compliance', name: 'Risk & Compliance', icon: '🛡️', steps: [
        { name: 'Basel III / OSFI Capital Adequacy Calculation', owner: 'Capital Management', output: 'CAR Report', priority: 'critical' },
        { name: 'LCR & NSFR Liquidity Metrics (LCR ≥ 100%)', owner: 'Treasury / ALM', output: 'Liquidity Report', priority: 'critical' },
        { name: 'ICAAP Stress Test Scenarios & Results', owner: 'Enterprise Risk', output: 'Stress Test Pack', priority: 'critical' },
        { name: 'AML / KYC Compliance Monitoring Report', owner: 'Compliance', output: 'AML Dashboard', priority: 'high' },
        { name: 'Internal Audit Finding Remediation Tracker', owner: 'Internal Audit', output: 'Audit Tracker', priority: 'high' },
        { name: 'Operational Risk Loss Event Register', owner: 'Op Risk', output: 'OR Register', priority: 'high' },
        { name: 'Model Risk Validation Summary', owner: 'Model Risk', output: 'Model Risk Report', priority: 'medium' },
        { name: 'IFRS 9 Staging & Expected Credit Loss Update', owner: 'Credit Risk', output: 'ECL Update', priority: 'critical' },
        { name: 'Regulatory Submission (FINREP / FR Y-9C)', owner: 'Reg Reporting', output: 'Reg Submission', priority: 'critical' },
        { name: 'Board Risk Committee Deck', owner: 'CRO Office', output: 'BRC Pack', priority: 'high' },
      ]},
      { id: 'corporate-banking', name: 'Corporate Banking', icon: '🏢', steps: [
        { name: 'Corporate Loan Portfolio Review & Internal Grading', owner: 'Corporate Credit', output: 'Portfolio Review', priority: 'critical' },
        { name: 'Syndicated Loan Participation & Agent Fee Tracking', owner: 'Syndication Finance', output: 'Syndication Report', priority: 'high' },
        { name: 'Cash Management & Treasury Services Revenue', owner: 'TM Finance', output: 'TM Revenue Report', priority: 'high' },
        { name: 'Trade Finance Utilisation & Exposure Report', owner: 'Trade Finance', output: 'TF Dashboard', priority: 'high' },
        { name: 'Project Finance Drawdown & Covenant Monitoring', owner: 'Project Finance', output: 'Covenant Tracker', priority: 'high' },
        { name: 'Corporate FX Hedging Program P&L Analysis', owner: 'FX Structuring', output: 'Hedge Report', priority: 'medium' },
        { name: 'Client Wallet & Share-of-Wallet Analysis', owner: 'Relationship Finance', output: 'Wallet Analysis', priority: 'medium' },
        { name: 'Cross-Sell Revenue Attribution Model', owner: 'Corporate Finance', output: 'Cross-Sell Dashboard', priority: 'medium' },
        { name: 'Committed vs Drawn Facility Utilisation', owner: 'Credit Operations', output: 'Facility Report', priority: 'high' },
        { name: 'RM P&L, Pipeline & Deal Closure Report', owner: 'Sales Finance', output: 'RM Dashboard', priority: 'medium' },
        { name: 'Corporate Banking Segment Close Pack', owner: 'Segment Controller', output: 'Segment Close Pack', priority: 'critical' },
      ]},
    ],
  },
  // ── HEALTHCARE & LIFE SCIENCES ─────────────────────────────────────────────
  {
    id: 'healthcare', name: 'Healthcare & Life Sciences', icon: '🏥',
    color: '#0d9488', bg: '#f0fdfa',
    description: 'Finance automation for hospitals, pharma, medical devices, and health insurance.',
    subCategories: [
      { id: 'hospital-finance', name: 'Hospital Finance', icon: '🏨', steps: [
        { name: 'Daily Patient Revenue Recognition & Payer Mix Analysis', owner: 'Revenue Cycle', output: 'Revenue Flash', priority: 'critical' },
        { name: 'Denial Management & AR Aging Report', owner: 'RCM Team', output: 'Denial Dashboard', priority: 'high' },
        { name: 'DRG / Case Mix Index Financial Analysis', owner: 'Finance Analytics', output: 'CMI Report', priority: 'high' },
        { name: 'OR Utilisation & Surgical Volume Revenue', owner: 'Surgical Finance', output: 'OR Dashboard', priority: 'high' },
        { name: 'Supply Chain & Drug Cost Per Adjusted Patient Day', owner: 'Supply Finance', output: 'Cost Per Patient', priority: 'medium' },
        { name: 'Labor Productivity (FTE per Adjusted Discharge)', owner: 'Workforce Finance', output: 'Labor Dashboard', priority: 'high' },
        { name: 'Capital Equipment Depreciation & Replacement Plan', owner: 'Asset Finance', output: 'Capex Plan', priority: 'medium' },
        { name: 'Charity Care & Bad Debt Reserve Estimation', owner: 'Community Finance', output: 'Charity Report', priority: 'medium' },
        { name: 'Clinical Service Line Profitability Analysis', owner: 'Service Line Finance', output: 'SL P&L', priority: 'high' },
        { name: 'CMS Cost Report & Regulatory Filing', owner: 'Compliance Finance', output: 'CMS Filing', priority: 'critical' },
        { name: 'Monthly CFO Dashboard & Board Pack', owner: 'CFO Office', output: 'CFO Pack', priority: 'critical' },
      ]},
      { id: 'pharma', name: 'Pharma & Biotech', icon: '💊', steps: [
        { name: 'R&D Spend Tracking by Compound & Clinical Phase', owner: 'R&D Finance', output: 'R&D Dashboard', priority: 'critical' },
        { name: 'Clinical Trial Budget vs Actual Variance', owner: 'Clinical Finance', output: 'Trial Finance Report', priority: 'high' },
        { name: 'Drug COGS & Gross Margin by SKU / Formulation', owner: 'Manufacturing Finance', output: 'COGS Report', priority: 'high' },
        { name: 'Patent Amortisation & IP Valuation Schedule', owner: 'IP Finance', output: 'IP Schedule', priority: 'medium' },
        { name: 'Milestone Payment Trigger Tracking', owner: 'Licensing Finance', output: 'Milestone Tracker', priority: 'high' },
        { name: 'Revenue by Product, Geography & Channel', owner: 'Commercial Finance', output: 'Revenue Tree', priority: 'high' },
        { name: 'Market Access & Rebate Reserve Calculation', owner: 'Pricing Finance', output: 'Rebate Model', priority: 'high' },
        { name: 'Pipeline NPV & Portfolio Valuation Model', owner: 'Strategy Finance', output: 'Pipeline NPV', priority: 'medium' },
        { name: 'SR&ED / R&D Tax Credit Claim Preparation', owner: 'Tax Finance', output: 'Tax Credit Claim', priority: 'high' },
        { name: 'Quarterly Investor Pack & Guidance Update', owner: 'Corp Finance', output: 'Investor Pack', priority: 'critical' },
      ]},
      { id: 'health-insurance', name: 'Health Insurance', icon: '📋', steps: [
        { name: 'Medical Loss Ratio (MLR) Calculation & Reporting', owner: 'Actuarial Finance', output: 'MLR Report', priority: 'critical' },
        { name: 'Premium Revenue vs Claims Incurred Flash', owner: 'Underwriting Finance', output: 'P&L Flash', priority: 'critical' },
        { name: 'IBNR Reserve Adequacy Assessment', owner: 'Actuarial', output: 'Reserve Report', priority: 'critical' },
        { name: 'Member Enrollment & Attrition Analysis', owner: 'Membership Finance', output: 'Enrollment Report', priority: 'high' },
        { name: 'Provider Contract & Network Cost Analysis', owner: 'Network Finance', output: 'Provider Report', priority: 'high' },
        { name: 'Risk Adjustment & ACA Corridor Calculation', owner: 'Risk Finance', output: 'Risk Adj Report', priority: 'high' },
        { name: 'Pharmacy Benefit Management Analytics', owner: 'PBM Finance', output: 'PBM Dashboard', priority: 'medium' },
        { name: 'Star Ratings ROI & Quality Bonus Accrual', owner: 'Quality Finance', output: 'Star Rating Report', priority: 'medium' },
        { name: 'State Filing & Regulatory Capital Surplus', owner: 'Compliance Finance', output: 'State Filing', priority: 'critical' },
        { name: 'Annual Report to Board & Audit Committee', owner: 'CFO Office', output: 'Annual Report Pack', priority: 'critical' },
      ]},
      { id: 'medtech', name: 'Medical Devices', icon: '🔬', steps: [
        { name: 'Product Revenue by SKU & Procedure Code', owner: 'Commercial Finance', output: 'Revenue Report', priority: 'high' },
        { name: 'Manufacturing Variance & Standard Cost Update', owner: 'Operations Finance', output: 'Mfg Variance', priority: 'high' },
        { name: 'FDA Clearance Capex Tracking (510k / PMA)', owner: 'Regulatory Finance', output: 'Reg Capex Tracker', priority: 'high' },
        { name: 'Service & Repair Revenue Recognition', owner: 'Service Finance', output: 'Service Revenue', priority: 'medium' },
        { name: 'Field Inventory & Consignment Valuation', owner: 'Inventory Finance', output: 'Field Inv Report', priority: 'medium' },
        { name: 'Capital Equipment Placement Profitability', owner: 'Capital Finance', output: 'Placement P&L', priority: 'high' },
        { name: 'Tender Pricing & Government Contract Margins', owner: 'Pricing Finance', output: 'Tender Analysis', priority: 'medium' },
        { name: 'Supply Chain Risk & Sole-Source Exposure', owner: 'Supply Finance', output: 'Risk Register', priority: 'high' },
        { name: 'Post-Market Surveillance Cost Tracking', owner: 'Quality Finance', output: 'PMS Cost Report', priority: 'medium' },
        { name: 'Earnings Release & Analyst Guidance Pack', owner: 'IR / Corp Finance', output: 'Earnings Pack', priority: 'critical' },
      ]},
      { id: 'cro', name: 'Life Sciences / CRO', icon: '🧬', steps: [
        { name: 'Contract Revenue Recognition (ASC 606 / IFRS 15)', owner: 'Revenue Finance', output: 'Rev Rec Schedule', priority: 'critical' },
        { name: 'Backlog & Pipeline Conversion Analysis', owner: 'Sales Finance', output: 'Pipeline Report', priority: 'high' },
        { name: 'Study-Level Profitability & Burn Rate', owner: 'Study Finance', output: 'Study P&L', priority: 'high' },
        { name: 'Pass-Through & Investigator Grant Tracking', owner: 'Grants Finance', output: 'Grant Tracker', priority: 'medium' },
        { name: 'FTE Utilisation & Billable Hours Analysis', owner: 'Resource Finance', output: 'Utilisation Report', priority: 'high' },
        { name: 'Client Change Order & Out-of-Scope Billing', owner: 'Contract Finance', output: 'CO Dashboard', priority: 'medium' },
        { name: 'Site Activation & Enrollment Spend Forecast', owner: 'Clinical Finance', output: 'Enrollment Forecast', priority: 'medium' },
        { name: 'Regulatory Milestone Billing Schedule', owner: 'Billing Finance', output: 'Billing Schedule', priority: 'high' },
        { name: 'Annual Operating Plan vs Actuals Variance', owner: 'FP&A', output: 'AOP Report', priority: 'high' },
        { name: 'Investor / Sponsor Financial Status Report', owner: 'Corp Finance', output: 'Sponsor Report', priority: 'critical' },
      ]},
    ],
  },
  // ── RETAIL & E-COMMERCE ────────────────────────────────────────────────────
  {
    id: 'retail', name: 'Retail & E-Commerce', icon: '🛒',
    color: '#d97706', bg: '#fffbeb',
    description: 'Retail finance automation from omnichannel revenue to margin and inventory analytics.',
    subCategories: [
      { id: 'omnichannel', name: 'Omnichannel Revenue', icon: '🌐', steps: [
        { name: 'Daily Sales Flash by Channel (In-Store / Online / App)', owner: 'Sales Finance', output: 'Daily Flash', priority: 'critical' },
        { name: 'Comparable Store Sales vs Prior Year', owner: 'Retail Analytics', output: 'SSSG Report', priority: 'high' },
        { name: 'Online GMV, Returns & Net Revenue Reconciliation', owner: 'E-Comm Finance', output: 'GMV Dashboard', priority: 'high' },
        { name: 'Basket Size, UPT & Conversion Metrics', owner: 'Merchandising Finance', output: 'Basket Analytics', priority: 'medium' },
        { name: 'Loyalty Program Revenue Attribution', owner: 'Loyalty Finance', output: 'Loyalty Report', priority: 'medium' },
        { name: 'Gift Card Breakage & Liability Tracking', owner: 'Revenue Finance', output: 'Gift Card Report', priority: 'medium' },
        { name: 'Promotion ROI & Markdown Effectiveness', owner: 'Pricing Finance', output: 'Promo ROI Report', priority: 'high' },
        { name: 'Returns & Refund Rate by Category', owner: 'Returns Finance', output: 'Returns Dashboard', priority: 'high' },
        { name: 'Revenue by Geography / Store Format', owner: 'Regional Finance', output: 'Geo Revenue Map', priority: 'medium' },
        { name: 'Weekly Sales Forecast vs Actuals', owner: 'FP&A', output: 'Forecast Report', priority: 'high' },
        { name: 'Monthly Retail P&L & Board Pack', owner: 'CFO Office', output: 'Retail P&L Pack', priority: 'critical' },
      ]},
      { id: 'supply-chain-retail', name: 'Supply Chain & Inventory', icon: '📦', steps: [
        { name: 'Inventory Valuation (FIFO / AVCO) Reconciliation', owner: 'Inventory Finance', output: 'Inv Valuation Report', priority: 'critical' },
        { name: 'Stock Turnover & Days Inventory Outstanding', owner: 'Supply Chain Finance', output: 'DIO Dashboard', priority: 'high' },
        { name: 'Vendor Cost Price Variance Tracking', owner: 'Procurement Finance', output: 'CPV Report', priority: 'high' },
        { name: 'Shrinkage, Waste & Obsolescence Reserve', owner: 'Inventory Control', output: 'Loss Report', priority: 'high' },
        { name: 'DC / Warehouse Cost Allocation per Unit', owner: 'Logistics Finance', output: 'Fulfilment Cost', priority: 'medium' },
        { name: 'Inbound Freight & Landed Cost Analysis', owner: 'Procurement Finance', output: 'Landed Cost Model', priority: 'medium' },
        { name: 'Category Margin Contribution After Supply Costs', owner: 'Category Finance', output: 'Category Margin', priority: 'high' },
        { name: 'Seasonal Buy Plan Budget vs Actuals', owner: 'Planning Finance', output: 'Buy Plan Report', priority: 'medium' },
        { name: 'Supplier Scorecard & Payment Terms Analysis', owner: 'AP Finance', output: 'Supplier Scorecard', priority: 'medium' },
        { name: 'Working Capital & Cash Conversion Cycle', owner: 'Treasury', output: 'CCC Dashboard', priority: 'high' },
      ]},
      { id: 'store-ops', name: 'Store Operations', icon: '🏪', steps: [
        { name: 'Store-Level P&L by Format & Tenure', owner: 'Store Finance', output: 'Store P&L', priority: 'high' },
        { name: 'Labor % of Sales & Scheduling Efficiency', owner: 'Workforce Finance', output: 'Labor Analytics', priority: 'high' },
        { name: 'Occupancy Cost & Rent-to-Sales Ratio', owner: 'Real Estate Finance', output: 'Rent Analytics', priority: 'medium' },
        { name: 'Shrink Rate by Store vs Network Benchmark', owner: 'Loss Prevention Finance', output: 'Shrink Report', priority: 'high' },
        { name: 'New Store ROI & Payback Period Analysis', owner: 'Development Finance', output: 'New Store ROI', priority: 'medium' },
        { name: 'Store Capex vs Maintenance Budget', owner: 'Facilities Finance', output: 'Capex Report', priority: 'medium' },
        { name: 'Sales per Sq Ft & Productivity Metrics', owner: 'Strategy Finance', output: 'Productivity Report', priority: 'medium' },
        { name: 'Energy & Utilities Cost per Store', owner: 'Facilities Finance', output: 'Energy Report', priority: 'medium' },
        { name: 'Store Closure / Rightsizing Financial Impact', owner: 'Strategy Finance', output: 'Closure Analysis', priority: 'high' },
        { name: 'Regional Manager P&L Accountability Report', owner: 'Retail Finance', output: 'RM P&L Pack', priority: 'high' },
      ]},
      { id: 'ecomm', name: 'E-Commerce & Digital', icon: '💻', steps: [
        { name: 'Customer Acquisition Cost (CAC) by Marketing Channel', owner: 'Digital Finance', output: 'CAC Dashboard', priority: 'high' },
        { name: 'ROAS by Ad Platform (Google / Meta / TikTok)', owner: 'Marketing Finance', output: 'ROAS Report', priority: 'high' },
        { name: 'Contribution Margin per Order (Net of Shipping)', owner: 'E-Comm Finance', output: 'Per-Order P&L', priority: 'critical' },
        { name: 'Subscription / Membership Revenue Tracking', owner: 'Subscription Finance', output: 'Sub Revenue Report', priority: 'high' },
        { name: 'Last-Mile Delivery Cost Optimisation', owner: 'Logistics Finance', output: 'LMD Analysis', priority: 'high' },
        { name: 'Cart Abandonment & Checkout Conversion Value', owner: 'CRO Finance', output: 'Conversion Report', priority: 'medium' },
        { name: 'Payment Processing Fees & Chargeback Rate', owner: 'Payments Finance', output: 'Payment Report', priority: 'medium' },
        { name: 'Influencer & Affiliate Commission Accrual', owner: 'Marketing Finance', output: 'Commission Accrual', priority: 'medium' },
        { name: 'Mobile App Monetisation & In-App Revenue', owner: 'Product Finance', output: 'App Revenue Report', priority: 'medium' },
        { name: 'LTV Cohort Analysis & CAC Payback Period', owner: 'Growth Finance', output: 'LTV Report', priority: 'high' },
      ]},
      { id: 'merchandise', name: 'Merchandising & Buying', icon: '🏷️', steps: [
        { name: 'Category Gross Margin % vs Plan', owner: 'Merchandising Finance', output: 'Category GM Report', priority: 'critical' },
        { name: 'Initial Markup (IMU) vs Realised Margin Bridge', owner: 'Buying Finance', output: 'IMU Report', priority: 'high' },
        { name: 'Private Label vs National Brand Margin Mix', owner: 'PL Finance', output: 'Brand Mix Report', priority: 'high' },
        { name: 'Markdown Cadence & Sell-Through Rate Analysis', owner: 'Planning Finance', output: 'Markdown Report', priority: 'high' },
        { name: 'OTB (Open-to-Buy) vs Actuals Dashboard', owner: 'Planning', output: 'OTB Dashboard', priority: 'medium' },
        { name: 'Supplier Rebate & Volume Discount Accrual', owner: 'Procurement Finance', output: 'Rebate Tracker', priority: 'medium' },
        { name: 'New Product Launch ROI & 90-Day Performance', owner: 'Launch Finance', output: 'Launch ROI', priority: 'high' },
        { name: 'Seasonal Clearance & End-of-Life Cost', owner: 'Inventory Finance', output: 'Clearance Report', priority: 'medium' },
        { name: 'Range Rationalisation Financial Impact Analysis', owner: 'Strategy Finance', output: 'Range Analysis', priority: 'medium' },
        { name: 'Buying Season Recap & Next Season Budget', owner: 'FP&A', output: 'Season Budget', priority: 'high' },
      ]},
    ],
  },
  // ── TECHNOLOGY & SAAS ──────────────────────────────────────────────────────
  {
    id: 'technology', name: 'Technology & SaaS', icon: '🚀',
    color: '#7c3aed', bg: '#f5f3ff',
    description: 'ARR / MRR tracking, R&D capitalisation, FinOps and investor-ready reporting for SaaS companies.',
    subCategories: [
      { id: 'saas-metrics', name: 'SaaS Core Metrics', icon: '📊', steps: [
        { name: 'ARR / MRR Waterfall (New, Expansion, Churn, Contraction)', owner: 'Revenue Finance', output: 'ARR Waterfall', priority: 'critical' },
        { name: 'Net Revenue Retention (NRR) & Gross Retention', owner: 'Customer Finance', output: 'NRR Dashboard', priority: 'critical' },
        { name: 'CAC by Channel & CAC Payback Period', owner: 'Growth Finance', output: 'CAC Report', priority: 'high' },
        { name: 'LTV / CAC Ratio by Cohort & Segment', owner: 'Analytics Finance', output: 'LTV:CAC Model', priority: 'high' },
        { name: 'Churn Analysis by Segment, Size & Tenure', owner: 'CS Finance', output: 'Churn Report', priority: 'critical' },
        { name: 'Magic Number & Sales Efficiency Score', owner: 'Sales Finance', output: 'Efficiency Report', priority: 'medium' },
        { name: 'Product-Led Growth (PLG) Funnel Revenue', owner: 'PLG Finance', output: 'PLG Dashboard', priority: 'high' },
        { name: 'Deferred Revenue & Revenue Recognition Schedule', owner: 'Revenue Finance', output: 'Rev Rec Schedule', priority: 'critical' },
        { name: 'Rule of 40 Tracking (Growth % + FCF Margin %)', owner: 'FP&A', output: 'Rule of 40 Report', priority: 'high' },
        { name: 'GAAP Financial Statements & Month-End Close', owner: 'Controller', output: 'GAAP Financials', priority: 'critical' },
        { name: 'Board Metrics Pack & Investor Update', owner: 'CFO Office', output: 'Board Pack', priority: 'critical' },
      ]},
      { id: 'rd-finance', name: 'R&D Finance', icon: '🔧', steps: [
        { name: 'R&D Capitalisation vs Expensing (ASC 730 / IAS 38)', owner: 'Technical Finance', output: 'R&D Cap Schedule', priority: 'critical' },
        { name: 'Engineering Headcount & Fully-Loaded Cost', owner: 'Engineering Finance', output: 'Headcount Report', priority: 'high' },
        { name: 'Cloud Infrastructure Spend by Environment (Dev/Prod)', owner: 'FinOps', output: 'Cloud Cost Report', priority: 'high' },
        { name: 'R&D % of Revenue vs Industry Benchmark', owner: 'FP&A', output: 'R&D Efficiency', priority: 'medium' },
        { name: 'Product Roadmap Investment by Feature Cluster', owner: 'Product Finance', output: 'Roadmap Finance', priority: 'medium' },
        { name: 'SR&ED / R&D Tax Credit Claim', owner: 'Tax Finance', output: 'Tax Credit Claim', priority: 'high' },
        { name: 'FinOps Unit Economics (Cost per API Call / User)', owner: 'FinOps', output: 'Unit Economics', priority: 'high' },
        { name: 'Technical Debt Cost Estimation', owner: 'Engineering Finance', output: 'Tech Debt Report', priority: 'medium' },
        { name: 'Technology Depreciation & Amortisation Schedule', owner: 'Asset Finance', output: 'Dep Schedule', priority: 'medium' },
        { name: 'Annual R&D Budget vs Plan Review & Reforecast', owner: 'R&D Finance', output: 'AOP Review', priority: 'high' },
      ]},
      { id: 'go-to-market', name: 'Go-to-Market Finance', icon: '🎯', steps: [
        { name: 'Pipeline Coverage & Weighted Revenue Forecast', owner: 'Sales Finance', output: 'Pipeline Report', priority: 'critical' },
        { name: 'Sales Quota Attainment & Commission Accrual', owner: 'Sales Comp Finance', output: 'Attainment Report', priority: 'high' },
        { name: 'Marketing Spend ROI by Campaign & Channel', owner: 'Marketing Finance', output: 'Marketing ROI', priority: 'high' },
        { name: 'Event & Field Marketing Cost Attribution', owner: 'Field Finance', output: 'Event ROI', priority: 'medium' },
        { name: 'Partnership & Channel Revenue Reporting', owner: 'Partner Finance', output: 'Partner Revenue', priority: 'medium' },
        { name: 'Win / Loss Cost Analysis by Segment', owner: 'Revenue Finance', output: 'Win/Loss Report', priority: 'high' },
        { name: 'Account Expansion & Upsell Revenue Tracking', owner: 'Account Finance', output: 'Expansion Report', priority: 'high' },
        { name: 'Territory Profitability Analysis', owner: 'Sales Finance', output: 'Territory P&L', priority: 'medium' },
        { name: 'SDR / BDR Productivity & Cost per Meeting', owner: 'Demand Gen Finance', output: 'SDR Productivity', priority: 'medium' },
        { name: 'GTM Efficiency Dashboard for CEO Review', owner: 'FP&A', output: 'GTM Dashboard', priority: 'high' },
      ]},
      { id: 'fp-and-a', name: 'FP&A & Planning', icon: '📐', steps: [
        { name: 'Rolling 12-Month Revenue Forecast', owner: 'FP&A', output: 'Rolling Forecast', priority: 'critical' },
        { name: 'Headcount Plan vs Actuals by Department', owner: 'HC Finance', output: 'Headcount Dashboard', priority: 'high' },
        { name: 'Burn Rate & Cash Runway Projection', owner: 'Treasury / FP&A', output: 'Runway Report', priority: 'critical' },
        { name: 'Operating Leverage & Margin Expansion Analysis', owner: 'FP&A', output: 'Margin Bridge', priority: 'high' },
        { name: 'Scenario Planning (Base / Bull / Bear)', owner: 'Strategy Finance', output: 'Scenario Models', priority: 'high' },
        { name: 'Department Budget Review & Variance Commentary', owner: 'FP&A', output: 'Budget Review', priority: 'high' },
        { name: 'Fundraising Data Room Financial Model', owner: 'Corp Finance', output: 'Data Room Model', priority: 'critical' },
        { name: 'Investor KPI Reporting (Monthly / Quarterly)', owner: 'CFO Office', output: 'Investor Report', priority: 'high' },
        { name: 'Cohort-Based Revenue Forecast', owner: 'Analytics Finance', output: 'Cohort Forecast', priority: 'medium' },
        { name: 'Annual Operating Plan (AOP) Build & CFO Sign-Off', owner: 'FP&A / CFO', output: 'AOP Deck', priority: 'critical' },
      ]},
      { id: 'finops', name: 'Cloud & FinOps', icon: '☁️', steps: [
        { name: 'Cloud Spend Allocation by Team & Product Line', owner: 'FinOps', output: 'Cloud Allocation', priority: 'high' },
        { name: 'Reserved Instance / Savings Plan Optimisation', owner: 'FinOps', output: 'RI Optimisation Report', priority: 'high' },
        { name: 'COGS vs R&D Cloud Split for Gross Margin Calc', owner: 'Revenue Finance', output: 'Cloud COGS Split', priority: 'critical' },
        { name: 'Cost per Customer / Cost per Transaction', owner: 'FinOps', output: 'Unit Cost Report', priority: 'high' },
        { name: 'Cloud Waste & Idle Resource Detection Report', owner: 'FinOps', output: 'Waste Report', priority: 'medium' },
        { name: 'SaaS Vendor Spend & Renewal Tracker', owner: 'Procurement Finance', output: 'Vendor Tracker', priority: 'medium' },
        { name: 'Data Egress & Transfer Cost Anomaly Detection', owner: 'FinOps', output: 'Anomaly Report', priority: 'medium' },
        { name: 'FinOps Maturity Assessment & Savings Realised', owner: 'FinOps', output: 'Maturity Report', priority: 'medium' },
        { name: 'Multi-Cloud Cost Comparison (AWS vs Azure vs GCP)', owner: 'Architecture Finance', output: 'Multi-Cloud Report', priority: 'medium' },
        { name: 'Cloud Capex vs Opex Treatment Analysis', owner: 'Technical Finance', output: 'Capex/Opex Report', priority: 'high' },
      ]},
    ],
  },
  // ── ENERGY & UTILITIES ─────────────────────────────────────────────────────
  {
    id: 'energy', name: 'Energy & Utilities', icon: '⚡',
    color: '#0284c7', bg: '#e0f2fe',
    description: 'Project finance, commodity risk, ESG reporting and regulatory compliance for energy companies.',
    subCategories: [
      { id: 'oil-gas', name: 'Oil & Gas', icon: '🛢️', steps: [
        { name: 'Production Volume vs Budget by Field & Well', owner: 'Operations Finance', output: 'Production Report', priority: 'critical' },
        { name: 'Lifting Cost per BOE Analysis', owner: 'Lifting Cost Team', output: 'Lifting Cost Report', priority: 'high' },
        { name: 'Commodity Price Sensitivity & Hedging P&L', owner: 'Treasury / Commodity', output: 'Hedge Report', priority: 'critical' },
        { name: 'Royalty & Production Tax Calculation', owner: 'Tax Finance', output: 'Royalty Report', priority: 'high' },
        { name: 'Capex Drilling Programme vs Authorisation for Expenditure', owner: 'Projects Finance', output: 'Capex Tracker', priority: 'high' },
        { name: 'Decommissioning Reserve & ARO Update', owner: 'Accounting', output: 'ARO Schedule', priority: 'high' },
        { name: 'Reservoir Depletion & Reserve Certification', owner: 'Engineering Finance', output: 'Reserve Report', priority: 'critical' },
        { name: 'JV Partner Cost & Revenue Reconciliation', owner: 'JV Finance', output: 'JV Report', priority: 'high' },
        { name: 'Pipeline Tariff & Midstream Revenue', owner: 'Midstream Finance', output: 'Midstream Report', priority: 'medium' },
        { name: 'Quarterly Investor & SEC / SEDAR Filing', owner: 'Corp Finance', output: 'SEC Filing Pack', priority: 'critical' },
      ]},
      { id: 'renewables', name: 'Renewables', icon: '🌱', steps: [
        { name: 'Generation Output vs P50 / P90 Forecast', owner: 'Asset Finance', output: 'Generation Report', priority: 'critical' },
        { name: 'Revenue per MWh by PPA / Merchant Mix', owner: 'Commercial Finance', output: 'Revenue Per MWh', priority: 'high' },
        { name: 'ITC / PTC Tax Credit Monetisation Model', owner: 'Tax Finance', output: 'Tax Credit Report', priority: 'critical' },
        { name: 'LCOE (Levelised Cost of Energy) by Project', owner: 'Project Finance', output: 'LCOE Model', priority: 'high' },
        { name: 'Green Certificate / REC Inventory & Revenue', owner: 'Environmental Finance', output: 'REC Report', priority: 'medium' },
        { name: 'Project Equity IRR & Debt Service Coverage Ratio', owner: 'Project Finance', output: 'DSCR Report', priority: 'critical' },
        { name: 'O&M Cost per MW vs Budget', owner: 'Operations Finance', output: 'O&M Report', priority: 'high' },
        { name: 'Transmission Access & Curtailment Cost', owner: 'Grid Finance', output: 'Curtailment Report', priority: 'medium' },
        { name: 'Battery Storage Dispatch & Revenue Optimisation', owner: 'Trading Finance', output: 'Storage Report', priority: 'medium' },
        { name: 'ESG Impact Metrics & Carbon Avoidance Report', owner: 'ESG Finance', output: 'ESG Report', priority: 'high' },
        { name: 'Developer Pipeline & Land Rights Valuation', owner: 'Development Finance', output: 'Pipeline Valuation', priority: 'medium' },
      ]},
      { id: 'utilities', name: 'Regulated Utilities', icon: '🔌', steps: [
        { name: 'Allowed Revenue vs Actual Revenue Requirement', owner: 'Regulatory Finance', output: 'Revenue Req Report', priority: 'critical' },
        { name: 'Rate Case Filing & Regulatory Asset Tracking', owner: 'Regulatory Affairs', output: 'Rate Case Pack', priority: 'critical' },
        { name: 'Capital Programme Delivery & CWIP Tracking', owner: 'Capital Finance', output: 'CWIP Report', priority: 'high' },
        { name: 'Depreciation & Return on Rate Base (RAB)', owner: 'RAB Finance', output: 'RAB Report', priority: 'high' },
        { name: 'SAIDI / SAIFI Reliability Metrics & Cost', owner: 'Reliability Finance', output: 'Reliability KPIs', priority: 'medium' },
        { name: 'Load Forecasting & Demand Response Revenue', owner: 'Grid Finance', output: 'Load Forecast', priority: 'high' },
        { name: 'Pension & OPEB Obligation Update', owner: 'Benefits Finance', output: 'Pension Report', priority: 'medium' },
        { name: 'Environmental Compliance Cost Tracking', owner: 'ESG Finance', output: 'Compliance Cost', priority: 'high' },
        { name: 'Customer Affordability & Bad Debt Provision', owner: 'Retail Finance', output: 'Affordability Report', priority: 'medium' },
        { name: 'FERC / Regulatory Annual Report Submission', owner: 'Regulatory Finance', output: 'FERC Report', priority: 'critical' },
      ]},
      { id: 'esg', name: 'ESG & Carbon Finance', icon: '🌍', steps: [
        { name: 'Scope 1 / 2 / 3 GHG Emissions Inventory', owner: 'ESG Team', output: 'GHG Inventory', priority: 'critical' },
        { name: 'Carbon Credit Purchase & Retirement Tracking', owner: 'Carbon Finance', output: 'Carbon Registry', priority: 'high' },
        { name: 'Carbon Price Sensitivity on Operating Costs', owner: 'Risk Finance', output: 'Carbon Sensitivity', priority: 'high' },
        { name: 'Net Zero Roadmap Capex & Opex Modelling', owner: 'Strategy Finance', output: 'NZ Finance Model', priority: 'high' },
        { name: 'TCFD Climate Risk Financial Disclosure', owner: 'ESG Finance', output: 'TCFD Report', priority: 'critical' },
        { name: 'Green Bond / Sustainability-Linked Loan Reporting', owner: 'Treasury / ESG', output: 'GSL Report', priority: 'high' },
        { name: 'Water & Waste Cost per Unit of Production', owner: 'Ops Finance', output: 'Resource Cost Report', priority: 'medium' },
        { name: 'ISSB / CSRD Sustainability Report Financial Inputs', owner: 'Corp Finance', output: 'ISSB Pack', priority: 'critical' },
        { name: 'ESG Score Improvement ROI Analysis', owner: 'Strategy Finance', output: 'ESG ROI', priority: 'medium' },
        { name: 'Biodiversity & Nature Risk Financial Impact', owner: 'Environmental Finance', output: 'Nature Risk Report', priority: 'medium' },
      ]},
      { id: 'energy-trading', name: 'Energy Trading', icon: '📉', steps: [
        { name: 'Daily Trading P&L by Commodity & Book', owner: 'Trading Finance', output: 'Daily P&L', priority: 'critical' },
        { name: 'Mark-to-Market Positions (Power / Gas / LNG)', owner: 'Valuation Control', output: 'MTM Report', priority: 'critical' },
        { name: 'Commodity VaR & Stress Test Results', owner: 'Risk Management', output: 'VaR Report', priority: 'critical' },
        { name: 'Spark Spread & Dark Spread Analysis', owner: 'Analytics Finance', output: 'Spread Report', priority: 'high' },
        { name: 'Counterparty Credit Limit Utilisation', owner: 'Credit Risk', output: 'Credit Report', priority: 'high' },
        { name: 'Physical & Financial Position Reconciliation', owner: 'Middle Office', output: 'Position Report', priority: 'high' },
        { name: 'Options Portfolio Greeks & Premium P&L', owner: 'Structuring Finance', output: 'Options Report', priority: 'high' },
        { name: 'Margin Call & Collateral Management Report', owner: 'Collateral', output: 'Margin Report', priority: 'high' },
        { name: 'Forward Curve Update & Price Consensus', owner: 'Analytics', output: 'Curve Update', priority: 'medium' },
        { name: 'Monthly Trading Book Reconciliation & P&L Attribution', owner: 'Finance Controller', output: 'Book Recon', priority: 'critical' },
      ]},
    ],
  },
  // ── MANUFACTURING ──────────────────────────────────────────────────────────
  {
    id: 'manufacturing', name: 'Manufacturing', icon: '🏭',
    color: '#0891b2', bg: '#ecfeff',
    description: 'Standard costing, production variance, supply chain finance and operational efficiency.',
    subCategories: [
      { id: 'cost-accounting', name: 'Cost Accounting', icon: '💰', steps: [
        { name: 'Standard Cost Roll-Up & Product Cost Card', owner: 'Cost Accounting', output: 'Cost Card', priority: 'critical' },
        { name: 'Manufacturing Variance Analysis (MPV / MUV / Labor)', owner: 'Cost Accounting', output: 'Variance Report', priority: 'critical' },
        { name: 'COGS Reconciliation to General Ledger', owner: 'Controller', output: 'COGS Recon', priority: 'critical' },
        { name: 'Overhead Absorption & Under / Over-Absorption Report', owner: 'Cost Accounting', output: 'Absorption Report', priority: 'high' },
        { name: 'Plant P&L by Cost Centre', owner: 'Plant Finance', output: 'Plant P&L', priority: 'high' },
        { name: 'Bill of Materials (BOM) Cost Accuracy Review', owner: 'Engineering Finance', output: 'BOM Review', priority: 'high' },
        { name: 'Work-in-Progress (WIP) Valuation', owner: 'Production Finance', output: 'WIP Valuation', priority: 'high' },
        { name: 'Scrap & Rework Cost Tracking', owner: 'Quality Finance', output: 'Scrap Report', priority: 'medium' },
        { name: 'Standard vs Actual Production Hours Analysis', owner: 'Operations Finance', output: 'Hours Analysis', priority: 'medium' },
        { name: 'Annual Standard Cost Update & Financial Impact', owner: 'Cost Accounting', output: 'Standard Cost Update', priority: 'critical' },
      ]},
      { id: 'operations-finance', name: 'Operations Finance', icon: '⚙️', steps: [
        { name: 'OEE (Overall Equipment Effectiveness) Cost Impact', owner: 'Ops Finance', output: 'OEE Report', priority: 'high' },
        { name: 'Capacity Utilisation & Idle Cost Analysis', owner: 'Production Finance', output: 'Capacity Report', priority: 'high' },
        { name: 'Capex Authorisation & Project Spend Tracking', owner: 'Capital Finance', output: 'Capex Dashboard', priority: 'critical' },
        { name: 'Maintenance Capex vs Opex Classification', owner: 'Asset Finance', output: 'Maintenance Report', priority: 'medium' },
        { name: 'Energy Cost per Unit of Production', owner: 'Utilities Finance', output: 'Energy Report', priority: 'medium' },
        { name: 'Make vs Buy Economic Analysis', owner: 'Strategy Finance', output: 'Make vs Buy', priority: 'high' },
        { name: 'Throughput & Bottleneck Cost Analysis', owner: 'IE Finance', output: 'Throughput Report', priority: 'high' },
        { name: 'Lean / Kaizen & Continuous Improvement Savings', owner: 'CI Finance', output: 'Savings Tracker', priority: 'medium' },
        { name: 'Asset Utilisation & Replacement Decision Model', owner: 'Asset Finance', output: 'Asset Model', priority: 'medium' },
        { name: 'Plant Productivity Benchmarking vs Peers', owner: 'Operations Finance', output: 'Benchmark Report', priority: 'medium' },
      ]},
      { id: 'procurement-finance', name: 'Procurement Finance', icon: '🤝', steps: [
        { name: 'Purchase Price Variance (PPV) Report', owner: 'Procurement Finance', output: 'PPV Report', priority: 'high' },
        { name: 'Supplier Spend Cube & Category Analysis', owner: 'Spend Analytics', output: 'Spend Cube', priority: 'high' },
        { name: 'Contract Savings Realisation vs Target', owner: 'Procurement', output: 'Savings Report', priority: 'high' },
        { name: 'Sole-Source & Single-Source Risk Register', owner: 'Risk Finance', output: 'Risk Register', priority: 'high' },
        { name: 'Payment Terms Optimisation (DPO / Early Pay)', owner: 'AP Finance', output: 'Payment Analytics', priority: 'medium' },
        { name: 'Supplier Financial Health Scorecard', owner: 'Supplier Finance', output: 'Supplier Score', priority: 'medium' },
        { name: 'Raw Material Commodity Hedge Programme', owner: 'Treasury', output: 'Commodity Hedge', priority: 'high' },
        { name: 'Freight & Logistics Cost per Unit', owner: 'Logistics Finance', output: 'Freight Report', priority: 'medium' },
        { name: 'Spend vs Budget by Category & Business Unit', owner: 'Procurement Finance', output: 'Spend vs Budget', priority: 'high' },
        { name: 'Annual Category Strategy Financial Business Case', owner: 'Category Finance', output: 'Category BCA', priority: 'medium' },
      ]},
      { id: 'supply-chain-mfg', name: 'Supply Chain', icon: '🔗', steps: [
        { name: 'Inventory Days on Hand (DOH) by Category', owner: 'Inventory Finance', output: 'DOH Report', priority: 'high' },
        { name: 'Slow-Moving & Obsolete (SLOB) Reserve Analysis', owner: 'Inventory Finance', output: 'SLOB Report', priority: 'high' },
        { name: 'Working Capital Bridge (Inventory / AR / AP)', owner: 'Treasury Finance', output: 'WC Bridge', priority: 'critical' },
        { name: 'Demand Forecast Accuracy & Cost of Forecast Error', owner: 'SC Finance', output: 'Forecast Accuracy', priority: 'high' },
        { name: 'Safety Stock Cost vs Service Level Trade-off', owner: 'Planning Finance', output: 'Safety Stock Model', priority: 'medium' },
        { name: 'DC Network Cost Modelling', owner: 'Logistics Finance', output: 'DC Network Model', priority: 'medium' },
        { name: 'Carrier Performance & Freight Rate Analysis', owner: 'Logistics Finance', output: 'Carrier Report', priority: 'medium' },
        { name: 'Inbound Freight & Customs Duty Tracking', owner: 'Trade Finance', output: 'Duty Report', priority: 'medium' },
        { name: 'End-to-End Supply Chain Finance Simulation', owner: 'SC Finance', output: 'SC Simulation', priority: 'high' },
        { name: 'Supply Chain Resilience Capex Business Case', owner: 'Strategy Finance', output: 'Resilience BCA', priority: 'high' },
      ]},
      { id: 'product-profitability', name: 'Product Profitability', icon: '📊', steps: [
        { name: 'SKU-Level Gross Margin Analysis', owner: 'Product Finance', output: 'SKU Margin Report', priority: 'critical' },
        { name: 'Product Line P&L (Gross to Operating Margin)', owner: 'Product Finance', output: 'Product P&L', priority: 'critical' },
        { name: 'Activity-Based Costing (ABC) by Product', owner: 'Cost Accounting', output: 'ABC Model', priority: 'high' },
        { name: 'New Product Introduction (NPI) ROI & Break-Even', owner: 'NPI Finance', output: 'NPI ROI', priority: 'high' },
        { name: 'Transfer Pricing Policy & Intercompany Margins', owner: 'Tax Finance', output: 'TP Study', priority: 'high' },
        { name: 'Price Elasticity & Volume / Price Bridge', owner: 'Pricing Finance', output: 'Price Bridge', priority: 'high' },
        { name: 'Channel Profitability (Direct vs Distributor)', owner: 'Channel Finance', output: 'Channel P&L', priority: 'high' },
        { name: 'End-of-Life (EOL) Product Financial Wind-Down', owner: 'Portfolio Finance', output: 'EOL Analysis', priority: 'medium' },
        { name: 'Product Portfolio Rationalisation Analysis', owner: 'Strategy Finance', output: 'Portfolio Analysis', priority: 'medium' },
        { name: 'Quarterly Product Review with Sales & Ops', owner: 'Product Finance', output: 'Product Review Deck', priority: 'high' },
      ]},
    ],
  },
];

// ─── Utility Functions ─────────────────────────────────────────────────────
function nowTime(): string {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function downloadCSV(ind: Industry, sub: SubCategory, steps: Step[], statuses: Status[]): void {
  const header = ['#', 'Deliverable', 'Owner', 'Output Package', 'Priority', 'Status'];
  const rows = steps.map((s, i) => [i + 1, s.name, s.owner, s.output, s.priority, statuses[i] || 'pending']);
  const csv = [header, ...rows].map(r => r.map(c => `"${c}"`).join(',')).join('\n');
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `FinanceSmith-${ind.name.replace(/\s+/g, '-')}-${sub.name.replace(/\s+/g, '-')}-${new Date().toISOString().split('T')[0]}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function downloadExcel(ind: Industry, sub: SubCategory, steps: Step[], statuses: Status[]): void {
  const priorityColor: Record<Priority, string> = {
    critical: '#5b21b6', high: '#92400e', medium: '#164e63',
  };
  const rows = steps.map((s, i) => `
    <tr style="background:${i % 2 === 0 ? '#f8f9ff' : '#ffffff'}">
      <td style="padding:7px 10px;border:1px solid #e2e8f0;color:#4b5563;font-weight:600">${i + 1}</td>
      <td style="padding:7px 10px;border:1px solid #e2e8f0;color:#1e1b4b">${s.name}</td>
      <td style="padding:7px 10px;border:1px solid #e2e8f0;color:#4b5563">${s.owner}</td>
      <td style="padding:7px 10px;border:1px solid #e2e8f0;color:#4b5563">${s.output}</td>
      <td style="padding:7px 10px;border:1px solid #e2e8f0;color:${priorityColor[s.priority]};font-weight:600;text-transform:uppercase;font-size:11px">${s.priority}</td>
      <td style="padding:7px 10px;border:1px solid #e2e8f0;color:#059669;font-weight:600;text-transform:uppercase;font-size:11px">${(statuses[i] || 'pending').toUpperCase()}</td>
    </tr>`).join('');
  const html = `<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">
  <head><meta charset="UTF-8"><style>body{font-family:Calibri,Arial,sans-serif}</style></head>
  <body>
    <h2 style="color:#4361ee;margin:0 0 4px">${ind.name} &rsaquo; ${sub.name}</h2>
    <p style="color:#6b7280;margin:0 0 16px;font-size:13px">Generated: ${new Date().toLocaleString()} &nbsp;|&nbsp; Total Deliverables: ${steps.length}</p>
    <table style="border-collapse:collapse;width:100%">
      <thead><tr style="background:#4361ee">
        <th style="padding:8px 10px;border:1px solid #3652c7;color:#fff;text-align:left;font-size:12px">#</th>
        <th style="padding:8px 10px;border:1px solid #3652c7;color:#fff;text-align:left;font-size:12px">Deliverable</th>
        <th style="padding:8px 10px;border:1px solid #3652c7;color:#fff;text-align:left;font-size:12px">Owner</th>
        <th style="padding:8px 10px;border:1px solid #3652c7;color:#fff;text-align:left;font-size:12px">Output Package</th>
        <th style="padding:8px 10px;border:1px solid #3652c7;color:#fff;text-align:left;font-size:12px">Priority</th>
        <th style="padding:8px 10px;border:1px solid #3652c7;color:#fff;text-align:left;font-size:12px">Status</th>
      </tr></thead>
      <tbody>${rows}</tbody>
    </table>
  </body></html>`;
  const blob = new Blob([html], { type: 'application/vnd.ms-excel;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `FinanceSmith-${ind.name.replace(/\s+/g, '-')}-${sub.name.replace(/\s+/g, '-')}-${new Date().toISOString().split('T')[0]}.xls`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function downloadPDF(): void {
  const style = document.createElement('style');
  style.id = 'print-override';
  style.textContent = `
    @media print {
      body { background: white !important; font-family: Arial, sans-serif; }
      .no-print { display: none !important; }
      .print-header { display: block !important; margin-bottom: 16px; }
      .fs-card { box-shadow: none !important; border: 1px solid #ccc !important; break-inside: avoid; }
      .fs-log { display: none !important; }
    }
  `;
  document.head.appendChild(style);
  window.print();
  setTimeout(() => {
    const el = document.getElementById('print-override');
    if (el) el.remove();
  }, 1000);
}

// ─── Main Component ────────────────────────────────────────────────────────
const FinanceSmith: React.FC = () => {
  const [industryId, setIndustryId] = React.useState<string>('banking');
  const [subCatId, setSubCatId] = React.useState<string>('retail-banking');
  const [statuses, setStatuses] = React.useState<Status[]>([]);
  const [isRunning, setIsRunning] = React.useState<boolean>(false);
  const [logs, setLogs] = React.useState<LogEntry[]>([]);
  const timerRef = React.useRef<ReturnType<typeof setInterval> | null>(null);
  const logIdRef = React.useRef<number>(0);
  const logRef = React.useRef<HTMLDivElement>(null);

  const industry = INDUSTRIES.find(i => i.id === industryId)!;
  const subCat = industry.subCategories.find(s => s.id === subCatId) ?? industry.subCategories[0];
  const steps = subCat.steps;

  const addLog = React.useCallback((tag: string, text: string) => {
    setLogs(prev => [{
      id: ++logIdRef.current,
      time: nowTime(), tag, text,
    }, ...prev].slice(0, 60));
  }, []);

  React.useEffect(() => {
    if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }
    setIsRunning(false);
    setStatuses(steps.map(() => 'pending'));
    addLog('SYSTEM', `Loaded: ${industry.name} › ${subCat.name} — ${steps.length} deliverables`);
  }, [subCatId, industryId]);

  const handleIndustry = (id: string) => {
    const ind = INDUSTRIES.find(i => i.id === id)!;
    setIndustryId(id);
    setSubCatId(ind.subCategories[0].id);
  };

  const handleRun = () => {
    if (isRunning) return;
    setIsRunning(true);
    setStatuses(steps.map(() => 'pending'));
    addLog('SYSTEM', `Starting workflow: ${subCat.name}`);
    let idx = -1;
    timerRef.current = setInterval(() => {
      setStatuses(prev => {
        const next = [...prev];
        if (idx >= 0 && idx < steps.length) {
          next[idx] = 'completed';
          addLog('STEP', `Completed: ${steps[idx].output}`);
        }
        idx++;
        if (idx >= steps.length) {
          clearInterval(timerRef.current!); timerRef.current = null;
          setIsRunning(false);
          addLog('SYSTEM', `All ${steps.length} deliverables completed.`);
          return next;
        }
        next[idx] = 'running';
        addLog('AGENT', `Executing: ${steps[idx].name}`);
        return next;
      });
    }, 1300);
  };

  const handleReset = () => {
    if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }
    setIsRunning(false);
    setStatuses(steps.map(() => 'pending'));
    addLog('SYSTEM', 'Workflow reset to initial state.');
  };

  const completed = statuses.filter(s => s === 'completed').length;
  const running = statuses.filter(s => s === 'running').length;
  const pending = statuses.filter(s => s === 'pending').length;
  const pct = steps.length ? Math.round((completed / steps.length) * 100) : 0;

  const priorityStyle = (p: Priority): React.CSSProperties => {
    if (p === 'critical') return { background: C.critBg, border: `1px solid ${C.critBorder}`, color: C.critText };
    if (p === 'high')     return { background: C.highBg, border: `1px solid ${C.highBorder}`, color: C.highText };
    return                       { background: C.medBg,  border: `1px solid ${C.medBorder}`,  color: C.medText };
  };

  const statusStyle = (s: Status): React.CSSProperties => {
    if (s === 'completed') return { background: C.completedBg, border: `1px solid ${C.completedBorder}`, color: C.completedText };
    if (s === 'running')   return { background: C.runningBg,   border: `1px solid ${C.runningBorder}`,   color: C.runningText };
    return                        { background: C.pendingBg,   border: `1px solid ${C.pendingBorder}`,   color: C.pendingText };
  };

  const tagColor = (tag: string) => {
    if (tag === 'SYSTEM') return { bg: C.violetLight, color: C.violet };
    if (tag === 'AGENT')  return { bg: C.skyLight,    color: C.sky };
    if (tag === 'STEP')   return { bg: C.tealLight,   color: C.teal };
    return { bg: C.amberLight, color: C.amber };
  };

  return (
    <div style={{ minHeight: '100vh', background: C.pageBg, fontFamily: '"Inter","Segoe UI",system-ui,sans-serif', color: C.text }}>

      {/* ── HEADER ── */}
      <header style={{ background: 'white', borderBottom: `1px solid ${C.border}`, padding: '0 32px', boxShadow: '0 2px 12px rgba(67,97,238,0.08)' }}>
        <div style={{ maxWidth: 1280, margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 64 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ width: 36, height: 36, borderRadius: 10, background: 'linear-gradient(135deg,#4361ee,#7c3aed)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18 }}>💡</div>
            <div>
              <div style={{ fontWeight: 700, fontSize: 17, letterSpacing: '-0.3px', color: C.text }}>FinanceSmith AI</div>
              <div style={{ fontSize: 11, color: C.textLight, letterSpacing: '0.04em', textTransform: 'uppercase' }}>Multi-Industry Finance Orchestrator</div>
            </div>
          </div>
          <div className="no-print" style={{ display: 'flex', gap: 8 }}>
            <button onClick={() => downloadCSV(industry, subCat, steps, statuses)}
              style={{ padding: '7px 14px', borderRadius: 999, border: `1px solid ${C.border}`, background: 'white', color: C.textMid, fontSize: 12, fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 5 }}>
              ⬇ CSV
            </button>
            <button onClick={() => downloadExcel(industry, subCat, steps, statuses)}
              style={{ padding: '7px 14px', borderRadius: 999, border: `1px solid ${C.emerald}`, background: C.emeraldLight, color: C.emerald, fontSize: 12, fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 5 }}>
              ⬇ Excel
            </button>
            <button onClick={downloadPDF}
              style={{ padding: '7px 14px', borderRadius: 999, border: 'none', background: `linear-gradient(135deg,#4361ee,#7c3aed)`, color: 'white', fontSize: 12, fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 5 }}>
              ⬇ PDF
            </button>
          </div>
        </div>
      </header>

      {/* ── INDUSTRY TABS ── */}
      <div className="no-print" style={{ background: 'white', borderBottom: `1px solid ${C.border}`, padding: '0 32px' }}>
        <div style={{ maxWidth: 1280, margin: '0 auto', display: 'flex', gap: 2, overflowX: 'auto' }}>
          {INDUSTRIES.map(ind => {
            const active = ind.id === industryId;
            return (
              <button key={ind.id} onClick={() => handleIndustry(ind.id)}
                style={{
                  padding: '14px 18px', border: 'none', background: 'transparent', cursor: 'pointer',
                  fontSize: 13, fontWeight: active ? 700 : 500,
                  color: active ? ind.color : C.textMid,
                  borderBottom: active ? `2.5px solid ${ind.color}` : '2.5px solid transparent',
                  whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: 7,
                  transition: 'all 0.15s',
                }}>
                <span style={{ fontSize: 16 }}>{ind.icon}</span>
                {ind.name}
              </button>
            );
          })}
        </div>
      </div>

      <div style={{ maxWidth: 1280, margin: '0 auto', padding: '24px 32px 40px' }}>

        {/* ── INDUSTRY HEADER ── */}
        <div style={{ marginBottom: 20, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <h2 style={{ fontSize: 22, fontWeight: 800, margin: 0, color: industry.color, display: 'flex', alignItems: 'center', gap: 8 }}>
              {industry.icon} {industry.name}
            </h2>
            <p style={{ margin: '4px 0 0', fontSize: 13, color: C.textMid }}>{industry.description}</p>
          </div>
          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
            {[
              { label: 'Total', value: steps.length, color: C.blue },
              { label: 'Completed', value: completed, color: C.emerald },
              { label: 'Running', value: running, color: C.sky },
              { label: 'Pending', value: pending, color: C.textLight },
            ].map(kpi => (
              <div key={kpi.label} style={{ background: 'white', border: `1px solid ${C.border}`, borderRadius: 10, padding: '8px 16px', textAlign: 'center', minWidth: 72 }}>
                <div style={{ fontSize: 20, fontWeight: 800, color: kpi.color }}>{kpi.value}</div>
                <div style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.06em', color: C.textLight, marginTop: 1 }}>{kpi.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* ── PROGRESS BAR ── */}
        <div style={{ background: 'white', borderRadius: 10, border: `1px solid ${C.border}`, padding: '10px 16px', marginBottom: 20, display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ fontSize: 12, fontWeight: 600, color: C.textMid, whiteSpace: 'nowrap' }}>Progress</span>
          <div style={{ flex: 1, height: 8, background: C.surfaceAlt, borderRadius: 999, overflow: 'hidden' }}>
            <div style={{ width: `${pct}%`, height: '100%', background: `linear-gradient(90deg,${industry.color},#7c3aed)`, borderRadius: 999, transition: 'width 0.4s ease' }} />
          </div>
          <span style={{ fontSize: 13, fontWeight: 700, color: industry.color, minWidth: 36 }}>{pct}%</span>
        </div>

        {/* ── SUB-CATEGORY TABS ── */}
        <div className="no-print" style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 20 }}>
          {industry.subCategories.map(sc => {
            const active = sc.id === subCat.id;
            return (
              <button key={sc.id} onClick={() => setSubCatId(sc.id)}
                style={{
                  padding: '7px 14px', borderRadius: 999, border: `1.5px solid ${active ? industry.color : C.border}`,
                  background: active ? industry.bg : 'white', color: active ? industry.color : C.textMid,
                  fontSize: 12, fontWeight: active ? 700 : 500, cursor: 'pointer',
                  display: 'flex', alignItems: 'center', gap: 6, transition: 'all 0.15s',
                }}>
                {sc.icon} {sc.name}
              </button>
            );
          })}
        </div>

        {/* ── MAIN LAYOUT ── */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 20 }}>

          {/* ── WORKFLOW TABLE ── */}
          <div className="fs-card" style={{ background: 'white', borderRadius: 16, border: `1px solid ${C.border}`, boxShadow: '0 1px 3px rgba(0,0,0,0.06),0 4px 16px rgba(67,97,238,0.06)', overflow: 'hidden' }}>
            <div style={{ padding: '16px 20px 14px', borderBottom: `1px solid ${C.border}`, display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'linear-gradient(135deg,#fafbff,#f8f0ff)' }}>
              <div>
                <div style={{ fontWeight: 700, fontSize: 15, color: C.text }}>{subCat.icon} {subCat.name}</div>
                <div style={{ fontSize: 11, color: C.textLight, marginTop: 2, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{steps.length} deliverables · {industry.name}</div>
              </div>
              <div className="no-print" style={{ display: 'flex', gap: 8 }}>
                <button onClick={handleReset} disabled={isRunning}
                  style={{ padding: '6px 14px', borderRadius: 999, border: `1px solid ${C.border}`, background: 'white', color: C.textMid, fontSize: 12, fontWeight: 600, cursor: isRunning ? 'not-allowed' : 'pointer', opacity: isRunning ? 0.5 : 1 }}>
                  ↺ Reset
                </button>
                <button onClick={handleRun} disabled={isRunning}
                  style={{ padding: '6px 16px', borderRadius: 999, border: 'none', background: isRunning ? C.surfaceAlt : `linear-gradient(135deg,${industry.color},#7c3aed)`, color: isRunning ? C.textLight : 'white', fontSize: 12, fontWeight: 700, cursor: isRunning ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}>
                  {isRunning ? '⏳ Running…' : '▶ Run Workflow'}
                </button>
              </div>
            </div>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                <thead>
                  <tr style={{ background: C.surfaceAlt }}>
                    {['#','Deliverable','Owner','Output Package','Priority','Status'].map(h => (
                      <th key={h} style={{ padding: '9px 10px', textAlign: 'left', fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', color: C.textLight, borderBottom: `1px solid ${C.border}`, whiteSpace: 'nowrap' }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {steps.map((step, i) => {
                    const st = statuses[i] || 'pending';
                    const isActive = st === 'running';
                    return (
                      <tr key={i} style={{ background: isActive ? C.runningBg : i % 2 === 0 ? 'white' : C.surfaceAlt, transition: 'background 0.3s' }}>
                        <td style={{ padding: '9px 10px', borderBottom: `1px solid ${C.border}`, color: C.textLight, fontWeight: 600, fontSize: 12 }}>{i + 1}</td>
                        <td style={{ padding: '9px 10px', borderBottom: `1px solid ${C.border}`, color: C.text, fontWeight: isActive ? 600 : 400, maxWidth: 320 }}>
                          {isActive && <span style={{ display: 'inline-block', width: 6, height: 6, borderRadius: '50%', background: C.sky, marginRight: 6, animation: 'pulse 1s infinite' }} />}
                          {step.name}
                        </td>
                        <td style={{ padding: '9px 10px', borderBottom: `1px solid ${C.border}`, color: C.textMid, whiteSpace: 'nowrap', fontSize: 12 }}>{step.owner}</td>
                        <td style={{ padding: '9px 10px', borderBottom: `1px solid ${C.border}`, color: C.textMid, whiteSpace: 'nowrap', fontSize: 12 }}>
                          <span style={{ background: C.blueLight, color: C.blue, borderRadius: 6, padding: '2px 7px', fontSize: 11, fontWeight: 600 }}>{step.output}</span>
                        </td>
                        <td style={{ padding: '9px 10px', borderBottom: `1px solid ${C.border}` }}>
                          <span style={{ ...priorityStyle(step.priority), borderRadius: 999, padding: '2px 8px', fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>{step.priority}</span>
                        </td>
                        <td style={{ padding: '9px 10px', borderBottom: `1px solid ${C.border}` }}>
                          <span style={{ ...statusStyle(st), borderRadius: 999, padding: '2px 8px', fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                            {st === 'completed' ? '✓ ' : st === 'running' ? '⟳ ' : ''}{st}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* ── AGENT LOG ── */}
          <div className="fs-log" style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{ background: 'white', borderRadius: 16, border: `1px solid ${C.border}`, boxShadow: '0 1px 3px rgba(0,0,0,0.06),0 4px 16px rgba(67,97,238,0.06)', flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
              <div style={{ padding: '14px 16px 12px', borderBottom: `1px solid ${C.border}`, background: 'linear-gradient(135deg,#fafbff,#f0f4ff)' }}>
                <div style={{ fontWeight: 700, fontSize: 14, color: C.text }}>Agent Activity Log</div>
                <div style={{ fontSize: 11, color: C.textLight, marginTop: 2 }}>Live orchestration feed</div>
              </div>
              <div ref={logRef} style={{ flex: 1, overflowY: 'auto', maxHeight: 460, padding: '8px 0' }}>
                {logs.length === 0 && (
                  <div style={{ padding: '24px 16px', textAlign: 'center', color: C.textLight, fontSize: 12 }}>No events yet. Press Run Workflow to start.</div>
                )}
                {logs.map(entry => {
                  const tc = tagColor(entry.tag);
                  return (
                    <div key={entry.id} style={{ padding: '7px 14px', borderBottom: `1px solid ${C.border}`, display: 'flex', gap: 8, alignItems: 'flex-start' }}>
                      <span style={{ fontSize: 10, color: C.textLight, minWidth: 52, paddingTop: 1 }}>{entry.time}</span>
                      <span style={{ fontSize: 9, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.06em', padding: '2px 6px', borderRadius: 4, background: tc.bg, color: tc.color, whiteSpace: 'nowrap', marginTop: 1 }}>{entry.tag}</span>
                      <span style={{ fontSize: 12, color: C.textMid, flex: 1, lineHeight: 1.4 }}>{entry.text}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* ── DOWNLOAD CARD ── */}
            <div style={{ background: 'white', borderRadius: 16, border: `1px solid ${C.border}`, boxShadow: '0 1px 3px rgba(0,0,0,0.06),0 4px 16px rgba(67,97,238,0.06)', padding: '16px' }}>
              <div style={{ fontWeight: 700, fontSize: 13, color: C.text, marginBottom: 10 }}>Export Deliverables</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                <button onClick={() => downloadCSV(industry, subCat, steps, statuses)}
                  style={{ padding: '9px 12px', borderRadius: 10, border: `1px solid ${C.border}`, background: C.surfaceAlt, color: C.textMid, fontSize: 12, fontWeight: 600, cursor: 'pointer', textAlign: 'left', display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontSize: 16 }}>📄</span>
                  <div><div>Download CSV</div><div style={{ fontSize: 10, color: C.textLight, fontWeight: 400 }}>Comma-separated values</div></div>
                </button>
                <button onClick={() => downloadExcel(industry, subCat, steps, statuses)}
                  style={{ padding: '9px 12px', borderRadius: 10, border: `1px solid ${C.emerald}`, background: C.emeraldLight, color: C.emerald, fontSize: 12, fontWeight: 600, cursor: 'pointer', textAlign: 'left', display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontSize: 16 }}>📊</span>
                  <div><div>Download Excel</div><div style={{ fontSize: 10, color: C.teal, fontWeight: 400 }}>Formatted .xls workbook</div></div>
                </button>
                <button onClick={downloadPDF}
                  style={{ padding: '9px 12px', borderRadius: 10, border: 'none', background: `linear-gradient(135deg,#4361ee,#7c3aed)`, color: 'white', fontSize: 12, fontWeight: 600, cursor: 'pointer', textAlign: 'left', display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontSize: 16 }}>🖨️</span>
                  <div><div>Download PDF</div><div style={{ fontSize: 10, color: 'rgba(255,255,255,0.7)', fontWeight: 400 }}>Print-optimised layout</div></div>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
        button:hover { opacity: 0.9; }
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: #f8f9ff; }
        ::-webkit-scrollbar-thumb { background: #c7d2fe; border-radius: 999px; }
        @media (max-width: 900px) {
          div[style*="grid-template-columns"] { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  );
};

export default FinanceSmith;
