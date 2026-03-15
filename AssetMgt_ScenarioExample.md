Sprott Oracle Enabled Finance Transformation – Foundational Phase Overview
Executive Summary: Sprott Asset Management has engaged PwC to re-implement and optimize key Oracle ERP Cloud financial modules as part of a Foundational Phase finance transformation. The project runs from March 23, 2026 through August 24, 2026, targeting a go-live on July 27, 2026. Using PwC’s AIRE methodology (Align–Innovate–Release–Evolve), the initiative will streamline and standardize Sprott’s core finance processes to close critical control, data quality, and compliance gaps by leveraging out-of-the-box Oracle Cloud configurations in General Ledger, Accounts Payable, Accounts Receivable, Fixed Assets, Cash Management, Intercompany, and Tax modules. The Functional Scope includes redesigning Sprott’s chart of accounts and legal entity/ledger structure, implementing automated tax and intercompany capabilities, deploying the full Accounts Receivable module (customer invoicing to cash application), and enhancing Accounts Payable, Fixed Assets, and Cash Management with standard features not previously utilized. The Technical Scope encompasses development of up to 10 custom reports, 2 key integrations with Sprott’s banking systems, 6 data conversions (e.g. customers, suppliers, prior balances), minimal custom extensions, and 7 approval workflows across AP, GL, FA, and AR processes. The project is divided into four phases with defined deliverables in each phase (Align, Innovate, Release, Evolve) and a joint governance structure to oversee execution. Key assumptions include active client participation, timely access to data and environments, a “design-by-exception” approach (minimizing customizations), and that Sprott handles data cleansing and end-user training responsibilities. Below is a detailed breakdown of the project scope and plan, organized for use by solution architects and technical teams in designing an Agentic AI-enabled ERP implementation framework. [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]



Project Background & Objectives
Sprott’s leadership initiated the Oracle Enabled Finance Transformation to modernize and strengthen its finance operations. The primary goals are to streamline finance processes, simplify the systems landscape, improve data visibility and transparency, and enable strategic capabilities for future growth. This foundational phase focuses on fixing critical control, data quality, and compliance gaps in the current Oracle E-Business Suite by optimizing the existing Oracle footprint and using standard Oracle Cloud configuration and leading practices wherever possible. [Sprott_SOW...3.0_Signed | PDF] [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]
PwC and Sprott have aligned on a transformation path to first stabilize and enhance the foundational finance systems before pursuing additional value-add initiatives in later phases. The Foundational Phase serves as a base for future improvements, delivering a well-controlled Oracle Cloud ERP foundation on which Sprott can build more advanced capabilities. Key objectives include: [Sprott_SOW...3.0_Signed | PDF], [Sprott - L...n services | Word]

Redesign the General Ledger (GL) and Legal Entity Structure: Simplify and reconfigure the Chart of Accounts, ledger and entity setup (with primary and secondary ledgers) to enable better financial control and reporting. [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]
Implement Critical Modules Not Previously in Use: Deploy Oracle Tax for automated indirect tax calculation & accounting in Accounts Payable/Receivable, and establish an end-to-end Intercompany processing solution for automated intercompany billing, matching, eliminations, and settlements within Oracle Cloud. [Sprott_SOW...3.0_Signed | PDF]
Extend Order-to-Cash and Procure-to-Pay Capabilities: Roll out the Accounts Receivable (AR) module to manage customer master data, billing, receipts, and collections internally (replacing manual processes). Enhance Accounts Payable (AP) and Cash Management (CM) with improved invoice processing, payments, and bank reconciliations, and reimplement Fixed Assets (FA) to replace spreadsheet-based processes with standard Oracle asset management functions. [Sprott_SOW...3.0_Signed | PDF] [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]
Leverage Standard Functionality to Address Gaps: Turn on underutilized features and configurations (e.g. AP invoice workflow approvals, automated reconciliations, multi-period accounting, etc.) to reduce manual work, improve audit trails, and shorten close cycles. The project follows a “configuration first” (design-by-exception) approach – custom extensions or non-standard solutions will only be considered if absolutely necessary to fill critical gaps. [Sprott - L...n services | Word], [Sprott - L...n services | Word] [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]

Out-of-Scope Items: Budgetary Control, Employee Expense Management, Advanced Collections, and further complex allocation logic are excluded from this phase’s scope. Their relevance will be evaluated during the Align phase and could be addressed in future phases if needed. [Sprott_SOW...3.0_Signed | PDF]
Functional Scope – In-Scope Modules & Key Configurations
The table below details the Oracle Financials Cloud modules and major configuration components included in this foundational phase. Only the listed modules and configurations are in scope; any other modules or features are considered out of scope unless explicitly noted: [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]





































Oracle ModuleKey Configuration Elements In-ScopeGeneral Ledger (GL)Ledger setup (primary & secondary ledgers) and security rules [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]; Legal entities defined and assigned to ledgers [Sprott_SOW...3.0_Signed | PDF]; Chart of Accounts (COA) structure and cross-validation rules [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]; Reporting hierarchies and financial segments for management/regulatory reporting [Sprott_SOW...3.0_Signed | PDF]; Currency revaluation rules [Sprott_SOW...3.0_Signed | PDF]; Allocation formulas to automate recurring allocations (standard allocations in system) [Sprott_SOW...3.0_Signed | PDF]; Journal approval rules/workflows for General Ledger entries [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]. (Note: Advanced budget control features are excluded.) [Sprott_SOW...3.0_Signed | PDF]IntercompanyIntercompany Organizations and Trading Partners setup [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]; Intercompany balancing rules for automatic out-of-balance corrections [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]; Intercompany transaction and billing configuration; Intercompany transaction approval workflows [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF] ensuring end-to-end automated processing and elimination of intercompany transactions.Accounts Receivable (AR)Receivables system options (operational parameters for AR) [Sprott_SOW...3.0_Signed | PDF]; Customer master data configurations (customer profiles) [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]; Receivable activities (e.g. adjustments, late charges) [Sprott_SOW...3.0_Signed | PDF]; Auto-accounting rules to derive GL accounts for revenue and receivables postings [Sprott_SOW...3.0_Signed | PDF]; Receipt classes & methods for customer payments [Sprott_SOW...3.0_Signed | PDF]; Aging methods for credit management [Sprott_SOW...3.0_Signed | PDF]; Collections setup for managing customer dunning & collections processes [Sprott_SOW...3.0_Signed | PDF].Accounts Payable (AP)Payables and invoice options (e.g. tolerances, matching rules) [Sprott_SOW...3.0_Signed | PDF]; Supplier master and supplier approval workflow (onboarding controls) [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]; Invoice approval workflow for AP invoices [Sprott_SOW...3.0_Signed | PDF]; Payment terms, formats, and templates (e.g. ACH, wire formats) [Sprott_SOW...3.0_Signed | PDF]; Payment processing options and bank interface setups [Sprott_SOW...3.0_Signed | PDF]; Hold and resolution codes for invoice exceptions [Sprott_SOW...3.0_Signed | PDF]; Employee expense processing (basic AP entry of expenses – note: full Expense Management module is out-of-scope) [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF].Fixed Assets (FA)Asset book configurations and controls (ledger, calendar, depreciation methods) [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]; Asset categories and asset key setups [Sprott_SOW...3.0_Signed | PDF]; Asset locations and key flexfield definitions [Sprott_SOW...3.0_Signed | PDF]; Depreciation rules & calendars (useful life, conventions) [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]; Asset Lease management settings (to handle leased assets) [Sprott_SOW...3.0_Signed | PDF]; Asset addition, adjustment, transfer, and retirement process configurations.Cash Management (CM)Bank account configurations in Oracle Cash Management [Sprott_SOW...3.0_Signed | PDF]; Bank statement formats and reconciliation rules for automated bank reconciliations [Sprott_SOW...3.0_Signed | PDF]; Bank codes setup and payment import formats (for integration with banks) [Sprott_SOW...3.0_Signed | PDF]; Cash positioning and forecasting configurations (within scope of optimizing current module usage).Tax (Oracle Fusion Tax)Tax geographies and zones setup for indirect tax applicability [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]; Tax regimes, tax jurisdictions, and tax rates configuration for relevant indirect taxes (e.g. HST/VAT) across AP and AR transactions [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]; Tax rules to determine taxability and accounting treatment for purchase and sales transactions. (Note: U.S. taxes are not included in this phase’s configuration and will be assessed during Align phase if needed.) [Sprott_SOW...3.0_Signed | PDF]
Functional Processes Addressed: These configurations support improved execution of core finance processes. In this phase, Sprott’s finance transformation will cover processes such as Record-to-Report (financial close and consolidation, leveraging the redesigned GL structure), Invoice-to-Pay (streamlined AP invoice processing through payment), Order-to-Cash (customer invoicing to cash application in AR), Fixed Asset Management, and Intercompany transaction processing. Each in-scope process will be aligned with Oracle Cloud leading practices, emphasizing standardization and elimination of manual workarounds. (For example, the “Invoice to Pay” process will be enhanced by implementing a centralized AP invoice intake mailbox with Oracle Intelligent Document Recognition (IDR) and automated approval workflows, replacing the current manual email-based coding and approval process.) [Sprott_SOW...3.0_Signed | PDF], [Sprott - L...n services | Word] [Sprott_Scope Summary | Word], [Sprott_Scope Summary | Word]
Technical Scope – Reports, Integrations, Conversions, Extensions, Workflows
In addition to core module configurations, PwC has planned for key technical components (often referred to as RICE-W objects – Reports, Integrations, Conversions, Extensions, and Workflows) to enable Sprott’s requirements:


Reports (Custom Reporting): Up to 10 custom financial reports will be developed using Oracle Business Intelligence Publisher (BIP), Oracle Transactional Business Intelligence (OTBI), or Financial Reporting Studio (FRS) as appropriate. The exact reports will be identified during the Align workshops, but likely include enhanced management reports and financial statements not delivered out-of-the-box. Standard Oracle Cloud reports and SmartView analytics will be leveraged wherever possible to minimize custom report development. [Sprott_SOW...3.0_Signed | PDF]


Integrations: Two key system interfaces are in scope, both leveraging Oracle Cloud’s integration tools (e.g. Oracle Integration Cloud or native REST/SOAP APIs):

INT-01 – Payment Files (Outbound to Bank): Automatically generate outbound disbursement payment files from Oracle Payables to Sprott’s banking partner for supplier payments (e.g. ACH or EFT files). [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]
INT-02 – Bank Statement Imports (Inbound to Oracle): Load incoming bank statements into Oracle Cash Management for automated bank reconciliation.
Both integrations are assessed as “Medium” complexity and will utilize Oracle Cloud’s standard integration capabilities (file-based data import and API tools). Sprott will involve its bank or third-party providers as needed for formats and connectivity, while PwC will prepare Functional Design Documents and support end-to-end testing of these interfaces. [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF] [Sprott_SOW...3.0_Signed | PDF]







Data Conversions: The following master and open transactional data will be migrated from legacy systems (existing Oracle EBS or other sources) into Oracle Cloud:






















































Conversion IDData EntityData TypeDescription / ScopeComplexityCON-01CustomersMaster DataCustomer master records (accounts) [Sprott_SOW...3.0_Signed | PDF]Low [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]CON-02SuppliersMaster DataSupplier (vendor) master records [Sprott_SOW...3.0_Signed | PDF]Medium [Sprott_SOW...3.0_Signed | PDF]CON-03Fixed AssetsMaster DataFixed Asset master records (asset register) [Sprott_SOW...3.0_Signed | PDF]Medium [Sprott_SOW...3.0_Signed | PDF]CON-05Prior-Year GL BalancesSummary BalancesGeneral Ledger balances for the prior 2 fiscal years [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]Medium [Sprott_SOW...3.0_Signed | PDF]CON-06Open AR InvoicesOpen TransactionsCustomer invoices receivable (including intercompany AR) that remain open/unpaid at cutover [Sprott_SOW...3.0_Signed | PDF]Low [Sprott_SOW...3.0_Signed | PDF]CON-07Open AP InvoicesOpen TransactionsSupplier invoices payable that remain open (unpaid) at cutover [Sprott_SOW...3.0_Signed | PDF]Medium [Sprott_SOW...3.0_Signed | PDF]
Conversion approach: PwC will utilize Oracle’s out-of-the-box import templates and tools for data migration wherever possible. PwC will provide Sprott with predefined data templates detailing the required fields and format for each data object (customers, suppliers, assets, etc.). Sprott is responsible for extracting and cleansing legacy data and populating these templates. PwC will perform up to three mock data loads into non-production instances to validate data quality and load processes: [Sprott_SOW...3.0_Signed | PDF] [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]

Mock Load 1: ~25% of data loaded during the Innovate phase (initial data extraction and load to test environment). [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]
Mock Load 2 (SIT load): ~50% of data loaded in the system integration testing phase. [Sprott_SOW...3.0_Signed | PDF]
Mock Load 3 (UAT load): 100% of data loaded to a test environment before production cutover. [Sprott_SOW...3.0_Signed | PDF]

A final Production Data Load will bring 100% of all required records into the live Oracle Cloud system during the cutover period. For each load, PwC will provide results and load reconciliation reports (statistics of records loaded, errors, and failure reasons) to assist Sprott in validating and correcting data. Sprott will perform detailed data validation on migrated data and address any data errors (data cleansing), while PwC will resolve any load issues caused by configuration defects. [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]


Extensions (Custom Enhancements): The project approach is to minimize custom extensions. During Align workshops, any functional gaps that cannot be met with native Oracle capabilities will be identified and alternative solutions considered first. Only if absolutely required, extensions (customizations) will be designed – these would likely be limited in number/scope due to the focus on standard solutions (no specific customizations are pre-defined in the SOW). This “design by exception” assumption is factored into pricing and scope, meaning significant custom development beyond the planned items would trigger the formal change control process. [Sprott_SOW...3.0_Signed | PDF]


Workflows (Approvals & Process Automation): The following approval workflows will be configured using Oracle Cloud’s native BPM Worklist tools to automate key approval processes. Each workflow’s necessity and rules will be validated during Align; design documents will then specify workflow steps, and PwC will configure and test the workflows for Sprott’s approval: [Sprott_SOW...3.0_Signed | PDF] [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]





















































Workflow IDWorkflow Name (Process Area)Description / PurposeComplexityWF01Supplier Creation Approval (AP)Approval workflow for new supplier onboarding (vendor master data approvals) [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF].Low [Sprott_SOW...3.0_Signed | PDF]WF02AP Invoice Approval (AP)Routing of supplier invoices for approval before payment [Sprott_SOW...3.0_Signed | PDF].Medium [Sprott_SOW...3.0_Signed | PDF]WF03Payment Approval (AP)*Approval for processing payments (e.g. payment batches or individual payment over threshold) [Sprott_SOW...3.0_Signed | PDF].Low [Sprott_SOW...3.0_Signed | PDF]WF04Journal Approval (GL)Approval of manual journal entries in General Ledger [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF].Low [Sprott_SOW...3.0_Signed | PDF]WF05Intercompany Transaction Approval (GL/Intercompany)Approval of intercompany journals or transactions initiated in GL [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF].Low [Sprott_SOW...3.0_Signed | PDF]WF06Fixed Asset Approval (FA)Workflow for asset additions or changes that require approval (e.g. asset capitalization) [Sprott_SOW...3.0_Signed | PDF].Low [Sprott_SOW...3.0_Signed | PDF]WF07AR Transaction Approval (AR)Approval for certain AR transactions (e.g. credit memos or adjustments) [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF].Low [Sprott_SOW...3.0_Signed | PDF]
All seven workflows are assessed as low or medium complexity (per Appendix C’s complexity definition). During Align, PwC will confirm if each workflow is needed and finalize the rules (conditions, approvers) for each. The workflows will then be configured using standard Oracle cloud workflow tools and tested for Sprott’s sign-off. [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF] [Sprott_SOW...3.0_Signed | PDF]


Project Phases & Methodology (AIRE)
The project will be executed in four phases following PwC’s AIRE methodology – Align, Innovate, Release, Evolve. This framework is a user-centric agile implementation approach taking the program from inception to stabilization: [Sprott_SOW...3.0_Signed | PDF]


Align (Mar 23 – Apr 17, 2026): Define and Design Phase. Confirm the solution scope, refine requirements, and establish the foundation for design. Key activities include project kickoff, requirement validation workshops, drafting of user stories and requirements traceability (fit/gap) matrices, and initial solution design decisions. The Align phase focuses on achieving a shared understanding of future-state processes and system capabilities before detailed build begins. [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]


Innovate (Apr 20 – Jun 12, 2026): Build and Unit Test Phase. Design, configure, and develop the agreed-upon solution components from Align. This includes configuring the Oracle Cloud environments, performing unit testing of configurations, developing any needed integrations and reports, executing data conversion mock loads, and conducting prototype “playback” sessions to demonstrate the system to users and gather feedback for iterative refinement. Initial knowledge transfer to Sprott’s process leads begins in this phase, through hands-on configuration reviews and prototype walk-throughs. [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]


Release (Jun 15 – Jul 10, 2026): Testing and Deployment Preparation Phase. Perform end-to-end solution testing and readiness tasks to ensure the system is ready for production. Activities include formal System Integration Testing (SIT) (covering end-to-end business scenarios), User Acceptance Testing (UAT) led by Sprott (with PwC support in defect resolution), end-user training (Sprott-led, with PwC preparing training materials and conducting “train-the-trainer” sessions), and final cutover planning and dry-run exercises. Any remaining configuration adjustments and defect fixes are completed. The Go-Live readiness assessment is carried out to formally approve deployment. [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]


Evolve (Jul 13 – Aug 24, 2026): Go-Live and Stabilization Phase. Transition the solution into production and provide post-go-live support. This includes final data conversion into Production, executing the cutover plan to switch from legacy systems to Oracle Cloud, actual go-live deployment of the Oracle ERP Cloud on the planned date, and a hypercare support period (approx. 4–6 weeks) where PwC assists with issue triage, defect fixes, and knowledge transfer to Sprott’s IT/finance teams. After this phase, the system is expected to be stable and handed over to Sprott’s internal teams for ongoing operations. [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF] [Sprott_SOW...3.0_Signed | PDF]




(The timeline above outlines the phase schedule and key activities. Dates are subject to refinement in the detailed project plan.) Each phase culminates in specific milestone deliverables and client sign-offs, which also align to the project’s billing milestones. The fixed-fee engagement of $500,000 is apportioned across these phase milestones (Align 25%, Innovate ~29%, Release ~24%, Evolve ~21%). [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]
Key Deliverables by Phase
Throughout the project, PwC will produce formal deliverables that capture designs, strategies, configurations, and test results – serving as critical inputs for both project governance and for training the Agentic AI system that will assist in the ERP implementation. The major deliverables per phase are summarized below (with their identification IDs from the SOW):


Align Phase Deliverables: Establish the foundational plans and requirements baselines for the project.









































Deliverable (ID)Description & Acceptance CriteriaDetailed Project Plan (AL01)High-level integrated project plan with timelines for all key phases, activities, and milestones [Sprott_SOW...3.0_Signed | PDF]. Clearly identifies phase start/end dates, major activities, and milestones (subject to refinement as the project progresses).Business Requirements Traceability Matrix (AL02)Comprehensive list of functional requirements (user stories), organized by process and stakeholder, with indication of whether each requirement is met by standard configuration (“Fit”) or is a gap requiring customization or process change [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]. Gaps are categorized by type (Report, Integration, Conversion, or Extension) for clarity [Sprott_SOW...3.0_Signed | PDF].Instance Strategy (AL03)Document defining the purpose and usage of each Oracle Cloud instance (e.g. Development, SIT, UAT, Production), including timing for instance provisioning, refreshes, code migration approach, and environment management processes [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]. Ensures a clear plan for how and when each environment will be readied and used during the project.Conversion Strategy (AL04)Document outlining the data migration approach – which historical data will be migrated (e.g. number of years of history, level of detail such as balances vs. transactions), source systems involved, tools and methods for extraction and loading, data transformation/cleansing approach, and validation processes [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]. Also specifies where non-migrated historical data will be archived or retained for reference.Testing Strategy (AL05)A comprehensive strategy (often delivered as a presentation or document) describing all testing cycles and their objectives [Sprott_SOW...3.0_Signed | PDF]. It defines the scope and approach for Unit Testing, System Integration Testing (SIT), User Acceptance Testing (UAT), and any other testing (e.g. performance or security testing if applicable). It details testing timelines, entry/exit criteria, responsibilities for test scenario development, defect management processes, and testing tools to be used [Sprott_SOW...3.0_Signed | PDF].Integration Strategy (AL06)High-level design of the integration architecture for the program [Sprott_SOW...3.0_Signed | PDF]. It includes an overview of all required system interfaces (in-scope integrations), the data flow between Oracle Cloud and external systems, integration methods (e.g. use of middleware or file transfers), and strategy for error handling and monitoring.Process Taxonomy & Flows (AL07)Future-state process maps and data flow diagrams for in-scope finance processes [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]. Typically developed to Level 3 process detail (and Level 4 for critical subprocesses), these flows incorporate leading practices and any necessary system interactions or controls. They serve as a blueprint for how processes like Procure-to-Pay, Record-to-Report, etc., will function in the new Oracle Cloud environment, including integrations and data inputs/outputs.Key Design Decisions (AL08)Documentation of major solution design decisions made during Align workshops [Sprott_SOW...3.0_Signed | PDF]. For each key decision (e.g., design of the COA and enterprise structure, choice of configuration options vs. custom solutions), this document captures the decision made, alternatives considered, impacts, and the rationale. This provides a reference for future phases and governance to prevent revisiting settled design questions.


Innovate Phase Deliverables: Capture the detailed design and configurations completed, and prepare for testing and deployment.

































Deliverable (ID)DescriptionDesign Documents (IN01)A set of functional design specifications (and where needed, technical design docs) for the configured solution and any extensions [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]. These may include business process design documents, configuration workbooks with design rationale, and any MD50/MD70 documents for custom development. They collectively provide a blueprint of the solution’s design.Deployment Plan – Draft (IN02)A preliminary Cutover/Deployment Plan in Excel or MS Project format [Sprott_SOW...3.0_Signed | PDF]. It outlines the tasks, sequence, and responsibilities for deploying the solution to production – including final data conversion steps, preparation activities, cutover weekend tasks, and post-go-live steps. The draft is created during Innovate and will be finalized in Release (RE01) after testing the cutover in mocks.Test Scenarios & Results (IN03)Document listing all test scenarios executed during the project (primarily in SIT) and a summary of test results [Sprott_SOW...3.0_Signed | PDF]. It shows which business scenarios were tested, the outcome of each (pass/fail), and references to defect logs. This ensures traceability that all requirements have been validated in the solution through testing.Configuration Workbooks – Draft (IN04)Draft Configuration Workbooks capturing the setup of each in-scope Oracle module [Sprott_SOW...3.0_Signed | PDF]. These workbooks detail all configuration steps and parameter values (for General Ledger, AP, AR, FA, Tax, etc.), serving as documentation of how the system is configured. Final updates (if any) will be made in Evolve (EV03).Functional & Technical Specifications for RICEFW (IN05)A consolidated document or set of documents enumerating all Reports, Integrations, Conversions, Extensions, and Workflows designed/built [Sprott_SOW...3.0_Signed | PDF]. It includes functional specs (business requirements and design approach for each item) and technical specs (logic, mappings, code or configuration details) for each RICEFW object delivered. This is essential for future reference and for the AI architecture to understand custom components.Innovate Phase Closure Report (IN06)A summary report marking the end of the Innovate phase [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]. It lists the configurations completed, all RICEFW objects developed, results of unit and integration tests, and any open defects or items deferred. It provides a checkpoint that the build is complete to the agreed scope and details any known issues or workarounds moving into the next phase.


Release Phase Deliverables: Finalize preparation for go-live and formally close testing phases.

























Deliverable (ID)DescriptionDeployment Plan – Final (RE01)The finalized cutover plan, updated from draft IN02 with results from mock cutover and testing [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]. It contains the detailed, step-by-step schedule for deployment, including data load sequences, reconciliation steps, technical cutover tasks, and responsible owners for each task during go-live.UAT Closure Report (RE02)Document summarizing the completion of User Acceptance Testing [Sprott_SOW...3.0_Signed | PDF]. It details the UAT scenarios executed, outcomes, any outstanding defects at UAT completion, and whether exit criteria for UAT were met. It also includes a plan to resolve any open critical issues before go-live [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]. Sprott’s sign-off of this report indicates acceptance of the system for go-live (contingent on addressing noted open items).Final Integrations & Reports Specifications (RE03)A compilation of final functional/technical specifications for any integrations and custom reports delivered [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]. This may be an updated version or addendum to IN05, focusing on the technical design and operating instructions for interfaces and reports (since these might have been adjusted during testing).Cutover Plan (RE04)A detailed Production Cutover Runbook listing each step, owner, start/end time, and prerequisites for the go-live event [Sprott_SOW...3.0_Signed | PDF]. It covers tasks from final data backups, production instance setup, data migration execution, validation checkpoints, cutover decision points, and post-go-live activities. (This may be combined with the Deployment Plan documents.)


Evolve Phase Deliverables: Ensure production environment is set up correctly and formally hand over the solution.





























Deliverable (ID)DescriptionProduction Configuration Complete (EV01)Confirmation that the Production environment is fully configured and aligned to the agreed design [Sprott_SOW...3.0_Signed | PDF]. Essentially a checklist or report verifying all configurations, security setup, and integrations are in place and production-ready prior to go-live.Final Data Conversion Executed (EV02)Completion of the Production data migration [Sprott_SOW...3.0_Signed | PDF]. All master and open transaction data successfully loaded into Oracle Cloud production, with reconciliation of record counts and any variances documented. This may include a final data conversion reconciliation report.Final Configuration Workbooks (EV03)The completed set of configuration workbooks, updated after go-live to reflect the actual production configuration of all modules [Sprott_SOW...3.0_Signed | PDF]. These serve as the final configuration baseline documentation for Sprott’s Oracle Cloud system and will be a key knowledge asset for the AI architecture to reference for environment specifics.Post Go-Live Support Completion (EV04)Delivery of post go-live support and transition documentation [Sprott_SOW...3.0_Signed | PDF]. This includes a log of issues encountered and resolved during the hypercare period, support handover documents, and knowledge transfer to Sprott’s support teams to enable them to manage the system.Close-Out Report (EV05)A comprehensive project closure report summarizing the overall project outcomes [Sprott_SOW...3.0_Signed | PDF]. It includes an overview of benefits achieved, final project metrics, lessons learned, and confirmation that all deliverables were completed and accepted. This document serves as an official closure of the SOW and is useful for feeding learnings into the continuous improvement (Evolve) stage or future phases.


The deliverables above will also be useful as input for an Agentic AI system – for example, the requirements matrix and design documents can train the AI on Sprott’s specific configurations and business rules, and the test results and support logs can help the AI anticipate common issues or inquiries in the new system.
Program Governance & Team Structure
A robust joint governance structure is in place to manage the project. There are three primary governance levels/committees with defined roles, meeting cadence, and participants: [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]





























Governance BodyFrequencyParticipants (Examples)Key ResponsibilitiesSteering Committee (Executive Leadership)As needed (Key phase gates or major issues)Sprott senior executives (project sponsor, CFO or Controller) and PwC engagement partner; other key project leaders by invitation [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF].Provides strategic direction and ensures alignment with enterprise objectives [Sprott_SOW...3.0_Signed | PDF]. Approves major scope or budget changes and the project charter [Sprott_SOW...3.0_Signed | PDF]. Resolves escalated high-impact risks or decisions that cannot be resolved at the project level [Sprott_SOW...3.0_Signed | PDF].Project Leadership Committee (Project Management Team)WeeklySprott Finance Transformation lead (e.g., Finance Lead), Sprott process owners and technical leads, PwC project manager and workstream leads, PwC engagement leadership as needed [Sprott_SOW...3.0_Signed | PDF].Provides tactical direction on execution. Monitors project progress, addresses weekly status, issues and roadblocks [Sprott_SOW...3.0_Signed | PDF]. Reviews risks and issues that could impact timeline or budget, and decides action plans or escalations as needed [Sprott_SOW...3.0_Signed | PDF]. Allocates resources and prioritizes activities to meet project objectives.Project Team (Operational Team)Daily (stand-ups)Sprott Process Leads & SMEs in each area (GL, AP, AR, etc.); Sprott Functional Lead (as needed); PwC functional and technical team members; other SMEs as required [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF].Manages day-to-day execution of project tasks and deliverables. Tracks daily progress and weekly targets [Sprott_SOW...3.0_Signed | PDF]. Discusses and resolves immediate issues, and identifies any concerns that need to be escalated to leadership [Sprott_SOW...3.0_Signed | PDF]. Ensures each team member is clear on their tasks and timelines.
Decision-Making & RACI: All project activities and deliverables have a RACI (Responsible, Accountable, Consulted, Informed) assignment defined, as documented in the SOW’s responsibility matrices. In general, PwC is responsible for execution of most implementation tasks (as “R”) while Sprott is accountable for providing inputs, making key decisions, and ultimately accepting deliverables (Sprott often in “A” role for final approval). For example, Sprott must approve final requirements and design decisions, provide timely data, and perform user acceptance testing, while PwC drives design, configuration, and testing activities with Sprott’s collaboration. This clear division of roles is critical for the Agentic AI architecture, which can be configured to assist Responsible parties (e.g., by preparing draft design documents, test cases, status reports) while keeping Accountable parties (Sprott’s leadership) informed and engaged at decision points. [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]
Communication and Issue Management: Regular status reporting and risk/issue management are built into the governance process. For example, the Project Leadership Committee will review progress and key risks weekly, and determine which issues need escalation to the Steering Committee or require formal change requests. A Change Control Process (described in SOW Appendix A) will be used to handle any changes in scope or major requirements – involving assessment of impact and approval by a Change Control Board (with members from Sprott and PwC leadership) before changes are implemented. The Agentic AI system can facilitate governance by tracking action items, analyzing status reports for risk signals, and ensuring decisions and changes are documented per the defined process. [Sprott_SOW...3.0_Signed | PDF] [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]
Assumptions and Constraints
The project is structured with several key assumptions to ensure a successful implementation. These assumptions must be understood by the design team (and any AI assistants) as they define boundaries and responsibilities for the solution:


Active Client Participation: Sprott will provide timely access to knowledgeable staff and actively participate in requirements gathering, design workshops, testing, and training activities. Quick feedback and sign-offs from Sprott on deliverables and key decisions are assumed to keep the project on schedule. [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]


Environment Provisioning: Sprott’s IT team will provision necessary Oracle Cloud environments (e.g., development, test instances) early in the project (within the first week) so that configuration work can begin on time. Sprott is responsible for ongoing maintenance of these cloud instances (applying patches, managing environments), while PwC will coordinate timing for refreshes and deployments as per the Instance Strategy. [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]


Data Extraction & Quality: Sprott will extract data from legacy systems and perform data cleansing prior to conversion loads. PwC will provide templates and perform the loads, but the accuracy and preparation of source data (e.g., removing duplicates, fixing data quality issues) is a client responsibility. Sprott will also conduct detailed data validation after each load to confirm the migrated data’s correctness, with issues fed back for cleanup or config adjustment. [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]


Design by Exception: The solution is to be built using standard Oracle Cloud capabilities as much as possible. It’s assumed that minimal custom extensions or custom code will be needed. Any requirements that cannot be met with configuration will either require a change in business process or will go through change control to consider additional effort for custom development. This assumption keeps the project within the fixed fee scope and aligns with best practices for Cloud (avoiding heavy customizations). The Agentic AI can leverage this principle by focusing on standard Cloud configuration knowledge and flagging requests that imply customization. [Sprott_SOW...3.0_Signed | PDF]


Technology & Licensing: All necessary Oracle Cloud software licenses and environments (for financials and integration tools) are expected to be in place and funded by Sprott – the SOW cost does not include Oracle licensing or any hardware/infrastructure costs. If any third-party tools or add-ons are required, Sprott will handle procurement and licensing. [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]


Oracle Standard Product Support: If any product bugs or Oracle SaaS issues are encountered, PwC will help identify and log them with Oracle, but PwC is not responsible for resolving defects in Oracle’s standard software or for delays those issues might cause. Additionally, performance tuning, penetration testing, and end-user change management are not part of PwC’s scope (these remain Sprott’s responsibility or separate efforts). [Sprott_SOW...3.0_Signed | PDF] [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]


Global Delivery Model: PwC may utilize a mixed onshore/offshore team. The SOW assumes continuity of key PwC personnel, but allows resource substitutions if needed, with equivalent skills, including use of PwC’s global delivery centers, as long as commitments (e.g., working in North American time zone for meetings) are maintained. [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]


Working Hours and Logistics: Work is planned with a normal working schedule (8 hours/day, 5 days/week). Meetings will mostly occur during Toronto business hours (EST), even if some PwC team members are offshore. Sprott will provide necessary facilities or virtual meeting infrastructure (e.g., MS Teams, SharePoint for collaboration) to support project work. In-person sessions will be arranged as needed (or virtual as required by any travel restrictions). [Sprott_SOW...3.0_Signed | PDF] [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]


These assumptions highlight areas where the Agentic AI should be configured with context about responsibilities and constraints – for example, recognizing that change management and end-user training are out of scope for PwC in this SOW and thus those tasks fall to Sprott. The AI assistant can be programmed to remind users when a request might fall into an out-of-scope area or requires a formal change request. [Sprott_SOW...3.0_Signed | PDF]
Client Responsibilities
The SOW clearly delineates several Key Client Responsibilities to ensure project success. In summary, Sprott is expected to: [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]


Provide Leadership and Decision Making: Assign a dedicated Project Manager/Finance Lead on the client side to coordinate Sprott’s activities and make timely decisions. Sprott’s management remains responsible for all final decisions and ensuring the project meets business needs. Sprott’s leadership must be available for steering committee meetings, issue resolution, and to sign off on key deliverables and design choices. [Sprott_SOW...3.0_Signed | PDF]


Ensure Resource Commitment: Identify and make available knowledgeable business process owners, subject matter experts (SMEs), and key users for each in-scope area (GL, AP, AR, etc.) to participate in workshops, testing, and training. The quality of the solution depends on timely input from these Sprott resources, and the SOW assumes their active involvement (with allocated time as needed each week for project activities). [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]


Data Preparation: Extract and prepare high-quality data from legacy systems for conversion. Sprott must perform or support data cleansing and provide “clean” datasets for loading (e.g., resolving duplicate or inconsistent records ahead of time). Sprott is also responsible for validating that the data in Oracle after each load is correct, and for signing off that the final production data migration is acceptable. [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]


Change Management & Training: Manage the organizational change aspects. Sprott will lead end-user training, including developing training materials (with input from process leads who receive knowledge transfer during the project) and conducting training sessions for end users prior to go-live. Sprott is also responsible for communications and stakeholder engagement to ensure user readiness (this SOW excludes a formal change management workstream). [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]


Testing and Acceptance: While PwC will assist in test preparation and execution, Sprott is responsible for User Acceptance Testing – including defining UAT scenarios (with PwC’s input), providing UAT testers (end users), executing UAT scripts, and formally approving the system for go-live. Sprott must also provide or confirm acceptance criteria for each deliverable and review deliverables within 5 business days of delivery, issuing acceptance or pointing out deficiencies promptly. Lack of response within the review period may be deemed acceptance per the SOW. [Sprott_SOW...3.0_Signed | PDF], [Sprott_SOW...3.0_Signed | PDF]


Infrastructure and Access: Set up and maintain project collaboration tools like Microsoft Teams and SharePoint for document sharing, and ensure PwC team members have appropriate access to Sprott’s systems and facilities as needed. Also, provide any necessary VPN/remote access, test data, and security permissions in Oracle Cloud to enable the PwC team to perform configuration and testing. [Sprott_SOW...3.0_Signed | PDF]


Understanding these responsibilities is important for designing an AI-driven project assistant. The Agentic AI can help monitor and remind the Sprott team of upcoming tasks and responsibilities (for instance, alerting if a deliverable hasn’t been reviewed within the 5-day window, or if data extracts are needed by a certain date). However, it must also recognize that ultimate accountability for these tasks lies with Sprott’s team – the AI should support but not override the client’s own project management duties.

By consolidating the project’s scope, plans, and expectations from all relevant Sprott SharePoint documentation (especially the Statement of Work v3.0), this report provides a comprehensive reference for the design of an Agentic AI architecture to support the Oracle ERP Cloud implementation. The structured information above – from functional configurations and technical interfaces to timelines, deliverables, and roles – can be ingested by an AI system (such as PwC’s Agentic AI platform) to enable an intelligent project assistant. Such an AI agent could, for example, use the requirements matrix and design documents to answer team questions about the solution, leverage the project plan and timeline to send proactive reminders, and utilize testing/issue data to predict and flag potential risks. This ensures that the AI architecture is grounded in the project’s critical details and can provide relevant, context-aware support to the implementation team, ultimately contributing to a smoother Oracle Cloud ERP deployment for Sprott. [Sprott_SOW...3.0_Signed | PDF] [PwC PoV Ge...n 2025 (1) | PowerPoint], [Sprott - O...tReview_v1 | PowerPoint]
SourcesConvert toWordProvide your feedback on BizChatYou said: GIVE ME THE LIST OF CONVERSIONSCopilot said: ResearcherThanks for your request! Just to make sure I understand what you're looking for:
Could you clarify what you mean by “conversions”? Are you referring to:

Currency conversions (e.g., USD to CAD)?
Unit conversions (e.g., inches to centimeters, pounds to kilograms)?
Business or sales conversions (e.g., lead-to-customer conversion rates)?
Data or file format conversions (e.g., PDF to Word, CSV to Excel)?
Something else entirely?

Let me know which type of conversions you’re interested in. Once I have that, I can get started. Or if you’d prefer I use my best judgement, just say “go ahead” and I’ll proceed.
Choose your report lengthShort1 to 5 pagesLong5+ pagesProvide your feedback on BizChatYou said: show me sprott branding of the documents in a promptCopilot said: ResearcherReasoning completed in 80 stepsSprott Branding Guidelines and Visual Identity
Sprott’s brand identity is defined by a unified “One Sprott” approach, with a consistent visual style across all internal and external communications. At the core is the Sprott logo, a distinctive wordmark (in dark teal color) that symbolizes the company’s cohesive presence across its various business lines. Sprott’s brand attributes are encapsulated in the tagline “Contrarian. Innovative. Aligned.”®, reflecting a culture that is contrarian in approach, innovative in solutions, and aligned with clients’ interests. The official Sprott Brand Guidelines (updated September 2022) provide detailed standards for using the logo, colors, typography, and document layouts to ensure all materials – from internal memos and presentation decks to external reports, websites, and marketing brochures – have a consistent and professional look in line with Sprott’s visual identity. [sprott.com] [sprott.com], [sprott.com]


Logo Usage and Identity
Logo & Placement: The primary Sprott logo is a wordmark of the company name in a proprietary font, rendered in Sprott’s signature dark teal color. This logo is the central element of Sprott’s visual identity and serves as the fundamental expression of the “One Sprott” brand initiative. All official Sprott communications – including presentation decks, reports, memos, brochures, regulatory documents, stationery, and digital media – should feature the Sprott logo prominently. The brand guidelines explicitly state that the firm presents itself as a single, unified entity, even though it operates multiple lines of business; the consistent use of the same Sprott logo across all materials is key to that unity. [sprott.com]
Logo Rules: To maintain visual integrity, the guidelines lay out strict rules for logo usage. The logo must never be altered or distorted – forbidden actions include rotating, stretching, adding drop-shadows or other effects, outlining, or placing it on busy backgrounds that reduce legibility. A clear space or “exclusion zone” equal to the height of the “Sprott” text (the logo’s x-height) should surround the logo on all sides to separate it from other text or graphics. The logo also has a minimum size requirement to ensure readability: it should not be reproduced smaller than approximately 2 cm in height in print, or 80 pixels high in digital formats. [sprott.com]
Color Variations: The preferred version of the Sprott logo is in the official dark teal color (see Color Palette below). In cases where color printing is not an option or a single-color format is needed (e.g. in black-and-white print materials or on a dark background), the logo may be used in black or in a reversed white version. Aside from these approved variants (teal, black, or white), no other colors or stylizations are allowed for the logo.
Tagline Usage: Sprott’s brand attributes are often communicated with the registered tagline “Contrarian. Innovative. Aligned.” This tagline may appear in branded materials (for example, at the end of marketing documents or advertisements) to reinforce Sprott’s core values. It should be presented exactly as shown, including the trailing registered trademark symbol. The tagline encapsulates the firm’s “personality” – being contrarian (taking unique approaches), innovative, and aligned with stakeholders’ interests. It serves as a concise motto to consistently position Sprott’s identity in communications. [sprott.com], [sprott.com] [sprott.com]
Color Palette and Design Elements
Sprott’s visual identity is defined by a specific color palette that must be applied to all designs, ensuring a consistent look whether in print or digital formats. The Brand Guidelines describe a hierarchical color system with Primary and Secondary palettes:


Primary Colors: Sprott’s two signature colors are Dark Teal and Gold. The Dark Teal is the dominant brand color – it’s used in the company logo and as a primary design color. Its specifications are PMS 7708 (Pantone Matching System) with the hex value #005670 (an RGB composition of 0, 86, 112). The complementary Gold is a vibrant golden-yellow used as an accent and secondary signature color (PMS 7548, approx. hex #FFC600). These two colors together immediately identify Sprott’s materials; for instance, Sprott’s website and many presentations use dark teal as a background or header color, with gold for highlights or graphs. In text, the word “Sprott” is usually shown in dark teal to reflect the logo color. [sprott.com]


Primary Shades: To support design flexibility, the primary colors above have tinted shades that can be used for backgrounds, charts, tables, or other graphic elements. For example, 25%, 50%, and 75% tints of Dark Teal are defined in the guidelines (e.g. a 25% tint yields a lighter steel blue at hex #BFD1D9). Similar tints of the gold may be used for lighter accents (e.g. a pale gold/beige at 25% intensity, hex #E7DECD) as needed. These lighter shades ensure designs remain on-brand while providing contrast and readability (for instance, using a light tint of teal for a slide background with dark teal text). [sprott.com], [sprott.com]


Secondary Colors: In addition to the two primary colors, Sprott’s palette includes a selection of complementary secondary colors for use when additional colors are necessary (for example, in complex charts, graphs or infographics, and marketing materials). These secondary colors are chosen to harmonize with the primary teal/gold scheme while offering a broader range for differentiation. The secondary palette includes: [sprott.com]

A deep charcoal gray (PMS Black 7, hex #3D3935) for neutral text or backgrounds. [sprott.com]
A rich red (PMS 1805, a deep red-maroon, hex #AF272F) and an orange-red (PMS 7625, a vibrant orange-red, hex #D64D4D) for emphasis or critical highlights. [sprott.com], [sprott.com]
An olive/golden brown (PMS 4505 and its tints, e.g. 100% PMS 4505 is a mustard-gold shade, hex #A58D42, with lighter tints such as 50% at hex #CFBF9C) which complements the primary Gold. [sprott.com], [sprott.com]
A mid-tone blue (PMS 660, hex #407CCA) and a purple (PMS 2592, hex #9B26B6) that can be used in charts or illustrations. [sprott.com], [sprott.com]
Another accent orange-brown tone (PMS 7571, hex #CB7D30) and a green (PMS 7739 C, hex #309B42) for additional variety in infographics or section highlights. [sprott.com]

All color usage should adhere to the “Color Usage” guidelines in the brand manual: the primary teal and gold (and their shades) are favored for major design elements, while secondary colors are to be used sparingly and for specific purposes (graphs, highlights, or when multiple distinguishing colors are needed). The overall look of Sprott’s materials tends to be clean and sophisticated, using ample white space with teal and gold as the key identifiers, complemented by neutral grays and the occasional use of the approved accent colors for variety. [sprott.com]


Typography (Fonts)
Consistent typography is another critical component of Sprott’s brand look. Sprott’s official corporate typefaces are Titillium and Frutiger LT Std: [sprott.com]


Titillium: A modern, clean sans-serif font family. In Sprott’s materials, Titillium (often in its SemiBold or ExtraLight weights) is recommended for headings and titles to create clear, professional headlines. This font conveys a contemporary and polished feel, aligning with Sprott’s innovative brand attribute. [sprott.com]


Frutiger LT Std: A classic humanist sans-serif font family (originally designed for readability), used for body text and longer passages in printed materials. Frutiger’s clarity at small sizes makes it suitable for detailed reports, brochures, and other text-heavy documents. The guidelines include multiple weights and styles of Frutiger (Light, Roman, Bold, Condensed, etc.) for use in various contexts (e.g., Light for standard body copy, Bold for subheadings). [sprott.com] [sprott.com], [sprott.com]


For everyday office applications and digital use, where the official fonts may not be available on all computers or email platforms, Arial is designated as the substitute font. This means that for Microsoft Word documents, PowerPoint slides, emails, and other electronic communications, text should be set in Arial (a widely available sans-serif) to approximate the look and ensure compatibility. This helps maintain a consistent appearance when Sprott employees or external recipients might not have Titillium or Frutiger installed. [sprott.com]
In practice, Sprott’s document templates are likely pre-formatted to use the correct fonts. For example, a Word template might default to Arial for normal text styles (to ensure universal access), while using Titillium or Frutiger in graphic elements or print-ready outputs. Ensuring typeface consistency across all materials is important for preserving the “cohesive feel” of the Sprott brand. [sprott.com]
Document Templates and Layout Standards
To help employees and partners produce on-brand materials, Sprott provides standardized document templates (for reports, presentations, letters, etc.) that incorporate the approved visual elements. These templates are designed in accordance with the brand guidelines so that users can create content without deviating from Sprott’s identity. Key aspects of Sprott’s document and presentation templates include:


Logo Placement & Page Layout: Official templates (such as Word document letterheads, memo templates, and PowerPoint slide decks) come pre-set with the Sprott logo placed in the correct position (often the top of the page or slide). The templates ensure the required white space around the logo is preserved and the logo appears at an appropriate size and resolution. For instance, Sprott’s official letterhead and envelope designs include the teal Sprott logo at the top, with the company’s mailing address (Royal Bank Plaza, Toronto) and contact information in the footer in the prescribed format and font. All external-facing documents (such as client reports, proposals, press releases) carry the Sprott logo and often a footer or header with the company’s contact details, formatted per brand standards. [sprott.com]


Color Scheme in Templates: The background, headings, tables, and graphical elements in templates are colored using the official palette. For example, the PowerPoint template likely uses Dark Teal as the background or accent for title slides and section headers, with Gold and other secondary colors applied in charts or graphics. Word report templates might use the dark teal for headings or cover pages, and gold or teal tints for table cells or graphical accents. This ensures any report or slide deck is immediately recognizable as a Sprott document by its colors. The templates also define styles for charts and tables that use the approved colors (for instance, Excel charts or PowerPoint graphs would default to the designated palette colors rather than random colors). This is in line with the guideline that primary shades should be used for tables, charts, and graphs. [sprott.com]


Typography and Styles: The document templates are configured to use approved fonts and text styles. In PowerPoint templates, placeholder text is typically set in Arial (for broad compatibility) or in the brand fonts if available, with predefined styles for titles, subtitles, bullet points, captions, etc., matching Sprott’s typographic hierarchy. Word templates for reports or letters define heading styles and body text in alignment with Sprott’s font guidelines (e.g., a Word report template might use Arial 11pt for body text and larger, bold Arial or Titillium for headings). These styles are built into the template to promote consistency in font usage and sizing across all documents.


Consistent Design Elements: Sprott’s layouts favor a clean, professional look with plenty of white space, aligning with financial industry best practices. Templates likely include guidelines for margins, spacing, and alignment. For example, the Brand Guidelines note that printed publications must be clear and consistent, meeting both brand and regulatory requirements – in practice, this means documents should not be cluttered, and required disclaimers or information (such as regulatory disclosures, legal footnotes, or © notices) should be placed in designated areas in a standard font size. The Sprott Asset Management LP address and contact info are typically included in official documents (as seen on the letterhead and business card samples) in a standardized format and location. [sprott.com] [sprott.com], [sprott.com]


In summary, Sprott’s branding guidelines ensure that whether one is preparing an internal presentation or a public-facing financial report, the visual identity remains consistent. All materials should feature the Sprott logo in the correct form (dark teal or approved variant) with proper spacing, use the official color palette (dominant dark teal with gold and complementary accents), and adhere to the prescribed fonts and layout standards. By following the Brand Guidelines, Sprott’s team can produce documents and presentations that look professional and on-brand, reinforcing the company’s image and values in every communication. [sprott.com], [sprott.com] [sprott.com]
Key Branding Elements Summary
The table below summarizes the key visual branding elements defined in Sprott’s Brand Guidelines (as of the latest update in September 2022):

























Brand ElementGuidelines & SpecificationsLogo UsageSprott Wordmark Logo in dark teal (PMS 7708) is the primary brand identifier and appears on all official documents, presentations, and communications [sprott.com]. Must be kept in original form (never distorted, recolored, or altered) with clear space around it equal to the logo’s x-height on all sides. The logo should not be smaller than 2 cm tall in print (≈80px tall on screen) to ensure legibility. Black or white versions of the logo may be used when color printing is not possible or against dark backgrounds. Sprott’s materials often include the tagline “Contrarian. Innovative. Aligned.”® to reinforce the brand attributes [sprott.com].Color PalettePrimary Colors: “One Sprott” identity is anchored by Dark Teal (the default logo color: PMS 7708, RGB 0-86-112, Hex #005670) and Gold (vibrant accent color, PMS 7548, RGB 255-198-0, Hex #FFC600) [sprott.com]. These signature colors are used prominently in designs (e.g. teal backgrounds, gold highlights). Primary Shades: Lighter tints of the dark teal and gold (25%, 50%, 75%) are defined for use in charts, tables, and subtle background fills (e.g. 25% teal is a light blue, Hex #BFD1D9) [sprott.com], [sprott.com]. Secondary Colors: A complementary palette to be used sparingly for variety – includes a dark charcoal gray (PMS Black 7, Hex #3D3935), deep red (PMS 1805, Hex #AF272F), orange-red (PMS 7625, Hex #D64D4D), blue (PMS 660, Hex #407CCA), green (PMS 7739, Hex #309B42), purple (PMS 2592, Hex #9B26B6), and several neutral or muted shades (e.g., grays and beige tones derived from the gold) [sprott.com], [sprott.com].TypographyTitillium Web and Frutiger LT Std are the official typefaces for Sprott [sprott.com]. Titillium (a modern sans-serif) is generally used for headings and titles, while Frutiger (a classic sans-serif) is used for body text in print documents for readability [sprott.com]. In day-to-day digital use and shared documents, Arial is the approved substitute font (since Titillium and Frutiger may not be available on all systems) [sprott.com]. Templates and styles are configured to use these fonts and standard font sizes to maintain consistency.Document Templates & LayoutStandard Templates: Sprott provides pre-formatted templates for common document types (e.g. Word report/letterhead templates and PowerPoint decks) that embed the correct logo, colors, and fonts according to the brand guide. This ensures all documents have a consistent layout and design. Layout Standards: Documents typically feature a clean, professional layout with the Sprott logo in the header or footer as required, ample white space, and the official color accents. The company address and contact details are included on letterheads and reports in a standardized format [sprott.com]. Presentations: Slide decks follow a Sprott-branded theme – for example, title slides and section headers may use the dark teal background with the logo, and content slides use the approved fonts (Arial for text) on a light background with teal and gold accents for graphic elements and highlights. All content and design elements are aligned with Sprott’s branding rules (e.g. using approved color codes for shapes and charts, avoiding off-brand fonts or colors) to maintain a unified look in every communication piece [sprott.com], [sprott.com].
<small><strong>Sources:</strong> Sprott Brand Guidelines (Updated Sept 2022)【1】; excerpts show official rules on logo usage, color specifications, and font guidance. The Sprott Brand Guidelines document (available via Sprott’s website) provides comprehensive details and examples (e.g. letterhead and business card layouts) to ensure all Sprott materials—internal and external—adhere to the company’s visual identity standards.</small> [sprott.com] [sprott.com], [sprott.com]
