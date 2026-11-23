# Product Requirements Document (PRD)

## AI-Powered PM/PjM Job Discovery and Career Intelligence Platform

**Document status:** Updated draft incorporating team decisions\
**Version:** 1.6\
**Date:** 16 November 2026\
**Primary and exclusive job-data source:** Authorized 104 Job Bank API access for searching and retrieving public vacancies, including job descriptions\
**Interface languages:** English and Traditional Chinese (繁體中文)\
**Primary audience:** University students, fresh graduates, entry-level
job seekers, and people exploring or transitioning into Product
Management and Project Management careers

------------------------------------------------------------------------

## Document Control

| Version | Date | Summary |
|---|---|---|
| 1.3 | 16 November 2026 | Consolidated product requirements; bilingual interface, themes, responsive design, and 104 API access decisions. |
| 1.4 | 16 November 2026 | Added Product Design Rationale; restricted external job-data sourcing to 104 API; expanded data cleaning, transformation, API integration, analytical methods, automated evaluation, and background batch processing; recorded selected technology direction. |
| 1.5 | 16 November 2026 | Added the revised Job Discovery Dashboard UI sketch and documented its visual components, interactions, evidence labels, and relationship to functional requirements. |
| 1.6 | 16 November 2026 | Added the end-to-end design rationale, UI, and technical data-pipeline flowchart as a standalone SVG deliverable; linked the flowchart from the PRD and clarified pipeline responsibilities. |

## Document Purpose and Source Integration

This PRD consolidates two working documents: `PRD Jay.md` and
`TP PMCS PRD.md`.

The consolidated product combines: - A focused job-discovery and
job-understanding experience: responsibility-based PM/PjM
classification, keyword and natural-language search, evidence-backed job
analysis, and multi-job comparison. - A career-exploration experience:
PM/PjM career guidance, competency insights, an experience-based
Career Fit Assessment, and a context-aware floating AI assistant.

Where the source documents conflict or do not provide enough
information, this PRD records the issue in **Section 18 --- Decisions
and Remaining Questions**. Team-confirmed decisions are distinguished
from technical details that still require verification.

## 1. Product Design Rationale

### 1.1 Product Vision

We aim to build an AI-powered PM/PjM Job Discovery and Career Intelligence Platform that helps people understand, explore, and prepare for careers in Product Management (PM) and Project Management (PjM).

Rather than functioning as another conventional job-search website, the platform focuses on helping users understand what these jobs actually involve. By combining authorized public job-market data from 104 Job Bank with AI-assisted analysis, the platform transforms complex job descriptions into clearer, structured, and evidence-based career information.

Our ultimate goal is to bridge the gap between job-market expectations and individual career development.

### 1.2 Target Audience

The primary target audience consists of:

- **University students** exploring potential career paths who may not yet understand the differences between PM and PjM.
- **Fresh graduates** preparing to enter the job market and understand employer expectations.
- **Early-career professionals and career explorers** considering entering or transitioning into Product Management or Project Management.

These users may have limited professional experience or insufficient knowledge of the practical responsibilities associated with these roles. The platform should therefore make job-market information accessible without requiring prior industry expertise.

### 1.3 Core Problem

The product addresses three connected problems:

1. **Job titles do not always reflect actual responsibilities.** Different companies may use the same title for substantially different positions. A position titled Product Manager may primarily involve project scheduling and resource coordination, while a differently titled position may carry product strategy and product-outcome responsibilities.
2. **Job descriptions are difficult to interpret and compare.** JDs often contain extensive information, technical terminology, and inconsistent formats. Students and early-career job seekers may struggle to identify actual responsibilities, required competencies, and employer expectations.
3. **Users lack a clear connection between job requirements and their own development.** Even after discovering relevant vacancies, users may not know how their experience and competencies relate to employer expectations or what they should improve.

### 1.4 Driving Design Philosophy

The product is guided by four principles:

1. **Responsibilities over Titles:** PM/PjM classification should be based primarily on the main object being managed and the position's ultimate responsibility, rather than its job title alone.
2. **Evidence over Assumptions:** AI-generated classifications, summaries, and competency analyses should be grounded in actual job-description content. Explicitly stated requirements must be distinguished from AI-inferred findings.
3. **Understanding over Information Overload:** Rather than simply presenting large amounts of job information, the platform should organize and explain that information so users can understand and compare opportunities.
4. **Career Development over Job Matching Alone:** The platform should help users understand employer expectations, reflect on demonstrated competencies, and identify potential areas for development—not merely find vacancies.

### 1.5 Product Design Approach

The platform implements this philosophy through three connected capabilities:

- **Job Discovery and Intelligence:** Retrieve authorized public vacancies from 104 Job Bank, organize job information, and classify PM/PjM positions based on their actual responsibilities.
- **AI-Assisted Job Understanding:** Use AI to summarize job descriptions, extract competencies, explain classification decisions, and support comparisons between vacancies.
- **Career Exploration and Development:** Provide career guidance, competency insights, and an experience-based Career Fit Assessment that connects users' self-reported experience with real job-market requirements.

Through these capabilities, the platform turns job-market information into practical career intelligence and helps users make more informed decisions about professional development.

### 1.6 UI/UX Design and Main Dashboard Sketch

The following revised dashboard sketch translates the product rationale into the primary Job Discovery experience. It is a visual design reference for the MVP interface and should be implemented consistently with the functional requirements in this PRD.

![PMCS 104 Job Insight — revised Job Discovery Dashboard](PMCS_104_Job_Insight_UI_Dashboard.png)

**Figure 1. Revised Job Discovery Dashboard (design reference).** The image illustrates the intended layout and visual hierarchy. Vacancy titles, company names, dates, summaries, and competency examples shown in the sketch are illustrative placeholders, not verified live records from 104 Job Bank.

#### 1.6.1 Dashboard structure

1. **Global navigation:** Product identity and navigation to Job Discovery, Career Guide, Competency Insights, and Career Fit Assessment.
2. **Language and theme controls:** A visible Traditional Chinese/English switch and light/dark mode control. The selected language and theme must remain consistent across pages.
3. **Job discovery search:** A search field supporting job titles, keywords, and natural-language queries, with a clear search action.
4. **Role classification filters:** PM, PjM, Hybrid, Unclear, and Other. Classification is based on the main management object and ultimate responsibility described in the vacancy, not the job title alone.
5. **Location and sorting controls:** Allow users to narrow the results by available location data and sort the result list using supported fields such as posting date.
6. **Job result cards:** Show the original job title, company, location, posting date, role classification, AI-generated responsibility summary, and a route to the full job detail view.
7. **Competency evidence labels:** Distinguish explicitly stated competencies (Explicit) from AI-inferred competencies (Inferred). Inferred items must be supported by evidence and must not be presented as direct employer requirements.
8. **Multi-job comparison:** Allow users to select vacancies and compare them through the dedicated comparison workflow.
9. **Data freshness and provenance:** Display 104 Job Bank as the exclusive external vacancy data source and show the last successful synchronization timestamp. The timestamp must reflect a successful update, not merely the scheduled run time.
10. **Floating AI Assistant:** Keep a persistent entry point available across the platform. Its answers must distinguish vacancy-specific information from general PM/PjM guidance.

#### 1.6.2 Key interactions

- Submitting a search or changing a supported filter refreshes the displayed vacancy results.
- Selecting a classification filter narrows results to that classification without changing the original job title.
- Selecting **View Details** opens the vacancy detail page, where users can inspect source information, the original job description, AI analysis, classification rationale, and competency evidence.
- Selecting **Compare** adds or removes a vacancy from the comparison selection. The comparison action becomes available when the selection meets the minimum required number of vacancies.
- Selecting a competency evidence item should expose its supporting job-description passage or explanation where available.
- The language and theme controls apply across all product pages and components.
- The floating AI Assistant uses the currently viewed vacancy as context when one is selected and provides general career guidance when no vacancy is selected.

#### 1.6.3 Relationship to the rest of the product

This sketch represents the **main Job Discovery Dashboard only**. It is not intended to replace the detailed page specifications and user flows already defined for Job Analysis, Multi-Job Comparison, Career Guide, Competency Insights, Career Fit Assessment, Agent Activity, or the floating AI Assistant. Those pages and workflows remain governed by the Information Architecture, Functional Requirements, User Flows, and User Interface and Experience Requirements sections of this PRD. Additional page-level sketches may be added as the interface is finalized.

### 1.7 Design Rationale, UI, and Technical Pipeline Overview

The standalone vector flowchart **`PMCS_Design_Rationale_UI_Technical_Pipeline.svg`** accompanies this PRD. It connects the product's design principles to the revised Job Discovery Dashboard and the technical pipeline required to deliver the experience.

![Design rationale, revised UI, and technical data pipeline](PMCS_Design_Rationale_UI_Technical_Pipeline.svg)

**Figure 2. End-to-end design and data pipeline.** The diagram is a conceptual architecture view, not a deployment topology or a claim that provider endpoints and permissions have been fully verified. It shows the agreed source, processing stages, backend integrations, analysis outputs, and user-facing presentation.

The flow is: **104 Job Bank API → data cleaning and transformation → backend API integration and PostgreSQL persistence → OpenAI-assisted analysis → React UI presentation.** The backend handles provider credentials and requests; the frontend does not call 104 or OpenAI directly. New or materially changed vacancies enter the background analysis queue after synchronization.

The user-facing layer applies the four design principles in Section 1.4: classify by responsibilities rather than titles, show evidence rather than unsupported assumptions, organize information for understanding, and connect job-market requirements to career development.

---

## 2. Executive Summary

The AI-Powered PM/PjM Job Discovery and Career Intelligence Platform
helps users understand Product Manager (PM) and Project Manager (PjM)
careers, discover relevant vacancies, interpret job descriptions (JDs),
and explore how their interests and self-reported competencies relate to
real job requirements.

The platform uses job information exclusively from 104 Job Bank through the authorized 104 Job Bank API to identify relevant vacancies and analyze their
actual responsibilities. AI assists with role classification,
plain-language summaries, evidence-backed competency extraction,
natural-language search, and comparisons across selected vacancies.

The platform also provides career-learning features. Users can learn the
practical differences between PM and PjM, explore competency patterns
across the collected vacancies, and complete a
Career Fit Assessment. Users provide information about their experience,
projects, and demonstrated competencies. AI maps that information to
competencies and requirements extracted from vacancies on 104, then
explains areas of alignment, partial alignment, gaps, and insufficient
evidence. A floating AI assistant also helps users understand PM/PjM
careers and ask questions about the vacancy currently being viewed.

The platform is not intended to replace 104, process job applications,
make hiring decisions, or guarantee that a recommended vacancy is
suitable.

**Core value proposition:**\
**Understand what PM/PjM jobs really involve, compare opportunities
using evidence, and turn job-market requirements into clearer
career-development insights.**

## 3. Background and Problem Statement

PM and PjM job titles are not used consistently across companies. A
vacancy titled "Product Manager" may focus mainly on schedules,
resources, and project delivery, while a vacancy with a different title
may carry genuine product strategy and product-outcome responsibilities.

Job descriptions can also be long, technical, and difficult for students
or early-career job seekers to interpret. Users may need to read many
listings individually to understand responsibilities, compare
requirements, and identify the competencies employers request.

Existing job platforms help users locate vacancies, but users may still
need to do much of the interpretation and comparison themselves.

### 2.1 User problems

Users need a clearer way to: 1. Understand the practical differences
between PM and PjM. 2. Find relevant vacancies without relying only on
job-title keywords. 3. Identify what a vacancy's role is actually
responsible for. 4. Understand long JDs through concise, faithful
summaries. 5. Identify required competencies and the evidence supporting
them. 6. Compare several vacancies, including vacancies with different
classifications. 7. Understand recurring competency requirements across
the available dataset. 8. Reflect on their interests and self-reported
competencies in relation to real job requirements.

### 2.2 Product opportunity

The platform connects job-market data, AI-assisted JD analysis,
structured job discovery, and career exploration in one workflow. Its
distinguishing value is not simply collecting PM/PjM job listings; it is
helping users understand and compare the responsibilities behind those
listings.

## 4. Product Vision, Goals, and Non-Goals

### 3.1 Product vision

Help users move from understanding PM/PjM roles to discovering relevant
vacancies and making more informed career-development decisions.

### 3.2 Product goals

1.  Collect and organize relevant PM/PjM and related vacancies through
    an approved data-access method.
2.  Classify vacancies based primarily on actual responsibilities,
    expected outcomes, and JD evidence.
3.  Preserve original job information and provide links back to the
    source.
4.  Support traditional keyword search, structured filters, and AI
    natural-language search.
5.  Summarize JDs in accessible language without changing their meaning.
6.  Extract and organize job-related competencies with evidence and
    clear uncertainty labels.
7.  Allow users to select and compare multiple vacancies, including
    cross-category comparisons.
8.  Explain PM and PjM career paths and show competency patterns in the
    collected dataset.
9.  Provide a Career Fit Assessment that compares user-submitted
    experience and demonstrated competencies with requirements in
    available 104 vacancies.
10. Provide a responsive, bilingual interface with light and dark
    themes.
11. Make data freshness, source coverage, and AI-analysis limitations
    visible.

### 3.3 Non-goals

The initial product will not: - Replace 104 Job Bank or reproduce its
complete recruitment workflow. - Submit applications or contact
employers on behalf of users. - Guarantee that a user will be hired or
that a recommendation is objectively suitable. - Make hiring decisions
or rank candidates for employers. - Present a self-assessment as a
validated psychological, personality, or professional certification
test. - Infer protected personal characteristics. - Collect data through
unauthorized scraping or bypass source access restrictions. - Guarantee
comprehensive coverage of every PM/PjM vacancy in Taiwan. - Invent
salary, benefits, responsibilities, competencies, or other information
missing from a source JD. - Treat AI classifications, inferences, or
recommendations as unquestionable facts.

## 5. Target Users and Use Cases

### 4.1 Primary user groups

-   University students exploring future career paths.
-   Fresh graduates preparing to enter the job market.
-   Entry-level job seekers looking for PM/PjM-related roles.
-   People considering a transition into product or project management.
-   Users who already understand PM/PjM but want to compare actual
    vacancies.

### 4.2 Persona A --- University student exploring careers

**Profile:** A student with an interest in business, technology, or
management who is unsure which PM/PjM path fits their interests.

**Needs:** - Simple explanations of PM and PjM. - Examples of real job
responsibilities. - A way to understand employer expectations. -
Guidance on competencies they may want to develop.

**Success outcome:** Understand the two career paths and identify
relevant opportunities and possible learning priorities.

### 4.3 Persona B --- Fresh graduate

**Profile:** A recent graduate actively looking for a first full-time
role.

**Needs:** - Searchable and understandable job listings. - Clear
summaries of job responsibilities and requirements. - A way to compare
multiple positions. - Direct links to original vacancies. - An
indication of how their self-reported competencies relate to job
expectations, if assessment is available.

**Success outcome:** Create a shortlist of relevant vacancies and
understand their requirements and possible gaps.

### 4.4 Persona C --- Early-career job seeker or career explorer

**Profile:** A person with some work, internship, or project experience
who is considering PM/PjM roles or a career transition.

**Needs:** - Role classification based on actual responsibilities. -
Comparisons across industries and job levels. - Competency analysis and
career exploration. - A way to understand transferable competencies.

**Success outcome:** Understand which roles align with their interests
and experience, and identify realistic next steps.

## 6. Product Principles

The following principles apply across the product:

1.  **Responsibilities over titles:** Classify vacancies based on the
    work and outcomes described, not the title alone.
2.  **Source data remains authoritative:** Original source information
    must be preserved and must not be overwritten by AI.
3.  **Evidence before conclusions:** AI-generated classifications and
    competency findings should be supported by JD evidence wherever
    possible.
4.  **Uncertainty is acceptable:** The system must be able to say that a
    detail cannot be determined.
5.  **Separate job facts from career guidance:** General PM/PjM
    knowledge must not be presented as a fact about a specific vacancy.
6.  **Explain recommendations:** Any career-fit result must show its
    basis and limitations.
7.  **Do not overstate dataset coverage:** Market-level insights must
    show the dataset scope and sample size.

## 7. PM/PjM Definitions and Role Classification

### 6.1 Core distinction

PM and PjM should be distinguished primarily by their **main object of
management and ultimate responsibility**, not by whether individual
tasks overlap.

Both roles may participate in requirements discussions, cross-functional
communication, and progress tracking. The presence of one shared task is
not enough to determine a role.

### 6.2 Product Manager (PM)

-   **Main management object:** The product.
-   **Ultimate responsibility:** Product value and outcomes; ensuring
    that the product solves the right problems and creates value for
    users or the business.
-   **Common responsibilities:**
    -   Product strategy and direction.
    -   User, customer, and market research.
    -   Requirements analysis and feature planning.
    -   Product roadmap and prioritization.
    -   Product lifecycle management.
    -   Measuring product outcomes and value.
-   **Core question:** "What product should we build, and why?"

### 6.3 Project Manager (PjM)

-   **Main management object:** The project.
-   **Ultimate responsibility:** Project objectives and delivery;
    ensuring that the project is completed within agreed scope, time,
    resources, and quality constraints.
-   **Common responsibilities:**
    -   Project planning and scheduling.
    -   Milestone and progress tracking.
    -   Resource, personnel, and budget coordination.
    -   Project risk and issue management.
    -   Cross-functional and stakeholder communication.
    -   Project deliverables and completion.
-   **Core question:** "How do we deliver the agreed work within the
    constraints?"

### 6.4 Proposed classification taxonomy

The following five-category taxonomy is proposed as the consolidated
default. It follows the more detailed classification framework in
`PRD Jay.md` and expands the four-label framework in `TP PMCS PRD.md`.

  -----------------------------------------------------------------------
  Category                            Definition
  ----------------------------------- -----------------------------------
  **PM**                              The role primarily manages a
                                      product and is accountable for
                                      product direction, requirements,
                                      prioritization, and product value
                                      or outcomes.

  **PjM**                             The role primarily manages a
                                      project and is accountable for
                                      planning, coordination, risk,
                                      constraints, and project delivery.

  **Hybrid**                          The role meaningfully carries both
                                      PM product-value responsibilities
                                      and PjM project-delivery
                                      responsibilities.

  **Unclear**                         The vacancy appears to be within
                                      the PM/PjM role scope, but the JD
                                      does not provide enough evidence to
                                      determine its primary
                                      responsibility.

  **Other**                           The vacancy is related to the
                                      PM/PjM domain but is substantively
                                      a different role. It may receive a
                                      related-domain tag, such as
                                      PM-related or PjM-related.
  -----------------------------------------------------------------------

**Scope screening:** Before assigning one of the five labels, the system
should determine whether the vacancy is relevant to the platform at all.
Vacancies unrelated to product or project management should be excluded
rather than placed in Unclear or Other.

**Other tags:** PM-related and PjM-related are descriptive tags, not
additional classification categories or similarity scores. The tag must
be supported by the actual responsibilities, not only by the job title.

### 6.5 Classification decision sequence

The AI should consider the following questions in order: 1. Is the
vacancy within the platform's PM/PjM-related scope? 2. What is the main
object being managed: a product, a project, or both? 3. What are the
vacancy's central responsibilities? 4. What outcomes is the role
ultimately accountable for? 5. Does it carry both product-value and
project-delivery responsibilities at a meaningful level? 6. Is there
enough JD evidence to support a classification?

### 6.6 Hybrid classification rules

-   A PM tracking development progress does not automatically make the
    role Hybrid.
-   A PjM participating in requirements discussions does not
    automatically make the role Hybrid.
-   Hybrid requires meaningful evidence of both product strategy/value
    responsibility and project planning/delivery responsibility.
-   The AI must not classify a role as Hybrid merely because the JD
    contains words such as "product," "project," "communication," or
    "progress."

### 6.7 Unclear classification rules

Use Unclear when the vacancy appears relevant to PM/PjM work but the
available JD is too limited, ambiguous, or incomplete to support a more
specific classification.

Do not use Unclear as a general category for unrelated vacancies or for
every record that the AI cannot process.

## 8. Information Architecture and Core Pages

The proposed website contains seven main pages. The Job Explorer and Job
Analysis experience form the core product. Career exploration features
extend that core.

### 7.1 Main navigation

1.  Overview
2.  Career Guide: PM or PjM?
3.  Job Explorer
4.  Job Analysis
5.  Competency Insights
6.  Career Fit Assessment
7.  Agent Activity

Global controls: - English / Traditional Chinese language switch. -
Light / Dark theme switch. - Responsive navigation for desktop, tablet,
and mobile. - Persistent floating AI assistant entry point.

### 7.2 Overview

**Purpose:** Introduce the platform and summarize the currently
collected dataset.

**Proposed content:** - Product introduction and primary calls to
action. - Total vacancies in the current dataset. - Vacancy counts by
classification. - Recently collected or updated vacancies. - Frequently
requested competencies, with sample size and dataset coverage. - A brief
PM/PjM comparison. - Last successful data update and a data-coverage
note. - Links to Career Guide and Job Explorer.

Market statistics must describe the platform's dataset, not imply
complete coverage of the Taiwanese job market.

### 7.3 Career Guide: PM or PjM?

**Purpose:** Explain the two career paths before users explore job
listings.

**Content:** - PM and PjM definitions. - Side-by-side comparison of
management object, responsibility, deliverables, and typical work. -
Examples of responsibilities. - Common and role-specific competencies. -
Explanation of Hybrid roles. - Reminder that responsibilities vary by
company and should be checked in the original JD.

**Primary actions:** Explore PM jobs; explore PjM jobs; continue to Job
Explorer.

### 7.4 Job Explorer

**Purpose:** Help users find relevant vacancies in the approved or
curated dataset.

**Search modes:** - Traditional keyword search. - Structured filters. -
AI natural-language search.

**Proposed filters:** - Classification: PM, PjM, Hybrid, Unclear,
Other. - Location. - Industry. - Experience requirement, when
available. - Salary range, when available and comparable. - Posting date
or last-checked date. - Employment type, when available. - Company or
job title.

**Natural-language search example:**

"Find PM jobs in Taipei with a monthly salary above NT\$50,000 and no
requirement for more than three years of experience."

The AI should translate the request into editable search conditions
before or alongside execution. Conditions should distinguish: -
**Structured-field filters:** Directly supported by stored fields, such
as location or salary. - **JD text evidence:** Conditions that require
checking the job description, such as whether the role manages direct
reports. - **Unknown or unsupported conditions:** Conditions that cannot
be confirmed from the available data.

If a condition is ambiguous or cannot be reliably filtered, the system
should ask a clarification question or explain the limitation. It must
not imply that an unknown field has been verified.

**Search result information:** - Original job title. - Company. -
Location and salary, if provided. - AI classification. - Concise
AI-generated summary. - Posting date and last-checked date, where
available. - Original source link. - Selection control for multi-job
comparison.

The primary results layout should be compact and scannable. It should
not replace the original job title with an AI-generated category name.

### 7.5 Job Analysis

**Purpose:** Help users understand one vacancy in greater depth.

**Minimum content:** - Original job title and company. - Original source
link. - Original JD in its source language. - AI classification and
classification rationale. - Evidence excerpts supporting the
classification. - Plain-language job summary. - Main responsibilities. -
Competencies identified in the JD. - Required/preferred status, when the
JD makes that distinction clear. - Evidence labels and supporting
excerpts. - Source-provided salary, location, experience, and other
relevant fields. - Missing-information notices.

The original JD must remain accessible alongside the AI analysis. AI
summaries and translations must not replace the original source text.

### 7.6 Competency Insights

**Purpose:** Show patterns in the competencies requested across the
vacancies currently held in the dataset.

**Proposed content:** - Frequently mentioned competencies. - Competency
patterns by PM, PjM, and Hybrid classification. - Competency patterns by
industry or experience level, if the dataset supports meaningful
comparisons. - Required versus preferred competency patterns, when
source JDs make this distinction clear. - Sample size, dataset date
range, and relevant filters.

**Limitations:** - Insights must be based on the collected dataset, not
represented as a complete market survey. - Small sample sizes must be
disclosed. - The system must not claim that a competency is universally
required based on a small or biased sample. - Inferred competencies must
be distinguishable from explicitly stated requirements.

### 7.7 Career Fit Assessment

**Purpose:** Let users reflect on their interests and self-reported
competencies and compare them with the requirements found in available
vacancies.

**Proposed stages:**

**Stage 1 --- Self-reflection and work preferences** - Areas of
interest. - Preferred work activities. - Relevant experience or project
exposure. - Career direction of interest.

**Stage 2 --- KSA self-assessment** - User self-rates selected
competencies. - Questions should be understandable to students and
early-career users. - The system should explain competency terms. -
Responses are self-reported and should not be treated as objectively
verified ability.

**Stage 3 --- Personal competency profile** - Summarize the user's
self-reported interests and competencies. - Allow users to review or
revise their answers. - Clearly distinguish user-provided information
from AI-generated interpretation.

**Stage 4 --- Vacancy comparison and recommendations** - Compare the
profile with analyzed vacancies. - Explain why a vacancy appears
relevant. - Identify matching areas and possible development areas. -
Show missing or unavailable information. - Link each recommendation to
the original vacancy and its analysis.

Any match indicator must be described as an exploratory comparison, not
a hiring probability or guarantee of suitability.

### 7.8 Agent Activity

**Purpose:** Provide visibility into data collection and AI-analysis
operations.

This page may be administrator-facing in the MVP. General users may only
need a concise freshness indicator.

**Possible information:** - Last successful data import or
synchronization. - Last AI-analysis time. - Number of new, changed,
duplicate, and potentially expired records. - Recent synchronization and
analysis logs. - Current operation status: successful, running,
partially successful, or failed. - Error information appropriate to the
intended audience.

## 9. Functional Requirements

Priorities: - **Must:** Required for the core usable product. -
**Should:** Valuable, but can follow the core release. -
**Could/Later:** Future enhancement or dependent on unresolved
decisions.

### 8.1 Data collection and lifecycle

  -----------------------------------------------------------------------
  ID                      Requirement             Priority
  ----------------------- ----------------------- -----------------------
  FR-001                  Import an initial       Must
                          dataset through an      
                          approved source-access  
                          method.                 

  FR-002                  Preserve original job   Must
                          fields and original JD  
                          content separately from 
                          AI-generated analysis.  

  FR-003                  Store the original      Must
                          source URL and source   
                          identifier when         
                          available.              

  FR-004                  Validate, normalize,    Must
                          and deduplicate records 
                          before creating or      
                          updating job records.   

  FR-005                  Record first-collected  Must
                          and last-checked        
                          timestamps where        
                          available.              

  FR-006                  Detect material changes Should
                          and re-run affected AI  
                          analysis when updated   
                          source content is       
                          available.              

  FR-007                  Mark a vacancy expired  Should
                          or inactive only when   
                          its status is verified  
                          by the source or an     
                          approved checking       
                          method.                 

  FR-008                  A failed or incomplete  Must
                          sync must not cause     
                          unverified records to   
                          be deleted or marked    
                          expired.                

  FR-009                  Run scheduled daily     Must
                          synchronization using
                          the authorized 104 API,
                          subject to documented
                          limits and operating
                          conditions.
  -----------------------------------------------------------------------

### 8.2 Role classification and AI analysis

  -----------------------------------------------------------------------
  ID                      Requirement             Priority
  ----------------------- ----------------------- -----------------------
  FR-010                  Screen whether a        Must
                          vacancy is within the   
                          platform's              
                          PM/PjM-related scope.   

  FR-011                  Classify in-scope       Must
                          vacancies as PM, PjM,   
                          Hybrid, Unclear, or     
                          Other.                  

  FR-012                  Base classification on  Must
                          responsibilities,       
                          management object,      
                          expected outcomes, and  
                          JD evidence---not title 
                          alone.                  

  FR-013                  Provide a concise       Must
                          classification          
                          rationale with          
                          supporting JD evidence. 

  FR-014                  Summarize the JD        Must
                          without adding          
                          responsibilities or     
                          changing its meaning.   

  FR-015                  Extract competencies    Must
                          from the JD and retain  
                          supporting evidence.    

  FR-016                  Distinguish explicit    Must
                          evidence from inferred  
                          competency signals.     

  FR-017                  Keep required and       Should
                          preferred competencies  
                          separate when the JD    
                          supports that           
                          distinction.            

  FR-018                  Record analysis date    Should
                          and model or analysis   
                          version.                

  FR-019                  Allow uncertain or      Must
                          incomplete analysis     
                          results rather than     
                          forcing a confident     
                          classification.         
  -----------------------------------------------------------------------

### 8.3 Search and filtering

  -----------------------------------------------------------------------
  ID                      Requirement             Priority
  ----------------------- ----------------------- -----------------------
  FR-020                  Support keyword search  Must
                          across configured       
                          source fields, such as  
                          job title and JD text.  

  FR-021                  Support filters for     Must
                          classification and      
                          available structured    
                          job fields.             

  FR-022                  Allow users to select   Must
                          multiple classification 
                          filters.                

  FR-023                  Support sorting by      Must
                          posting date, newest    
                          first, where the source 
                          provides dates.         

  FR-024                  Support AI              Should
                          natural-language search 
                          by parsing user         
                          requests into search    
                          conditions.             

  FR-025                  Show parsed             Should
                          natural-language search 
                          conditions and allow    
                          users to edit them.     

  FR-026                  Distinguish             Should
                          structured-field        
                          filters, JD text        
                          evidence, and unknown   
                          conditions.             

  FR-027                  Ask for clarification   Should
                          or explain limitations  
                          when a search condition 
                          is ambiguous or         
                          unsupported.            
  -----------------------------------------------------------------------

### 8.4 Job results and detail

  -----------------------------------------------------------------------
  ID                      Requirement             Priority
  ----------------------- ----------------------- -----------------------
  FR-028                  Display the original    Must
                          job title, not an       
                          AI-rewritten title.     

  FR-029                  Display company,        Must
                          location, salary, and   
                          other source fields     
                          when available.         

  FR-030                  Display AI              Must
                          classification and a    
                          concise summary when    
                          analysis is available.  

  FR-031                  Provide a direct link   Must
                          to the original         
                          vacancy.                

  FR-032                  Allow users to open a   Must
                          detailed job analysis.  

  FR-033                  Display "Not provided"  Must
                          or an equivalent notice 
                          for missing source      
                          fields.                 

  FR-034                  Preserve access to the  Must
                          original JD alongside   
                          AI summaries or         
                          translations.           
  -----------------------------------------------------------------------

### 8.5 Multi-job selection and comparison

  -----------------------------------------------------------------------
  ID                      Requirement             Priority
  ----------------------- ----------------------- -----------------------
  FR-035                  Allow users to select   Must
                          multiple vacancies from 
                          search results.         

  FR-036                  Display the number of   Must
                          selected vacancies.     

  FR-037                  Allow users to start an Must
                          AI comparison of        
                          selected vacancies.     

  FR-038                  Allow cross-category    Must
                          comparison; users must  
                          not be forced to select 
                          only one                
                          classification.         

  FR-039                  Group vacancies by      Must
                          their original AI       
                          classification before   
                          comparing them.         

  FR-040                  Compare commonalities   Must
                          and differences within  
                          each classification     
                          group.                  

  FR-041                  Provide a final         Must
                          cross-category          
                          synthesis explaining    
                          differences in          
                          responsibilities and    
                          role direction.         

  FR-042                  Preserve classification Must
                          differences; do not     
                          force Other or Unclear  
                          vacancies into PM/PjM.  

  FR-043                  Include source          Must
                          references or original  
                          vacancy links for       
                          comparison findings.    

  FR-044                  Include                 Must
                          responsibilities,       
                          evidence-backed         
                          competencies, salary    
                          comparisons when        
                          comparable, and missing 
                          information where       
                          relevant.               
  -----------------------------------------------------------------------

### 8.6 Career guidance and competency insights

  -----------------------------------------------------------------------
  ID                      Requirement             Priority
  ----------------------- ----------------------- -----------------------
  FR-045                  Explain PM and PjM      Must
                          definitions and their   
                          practical differences.  

  FR-046                  Explain Hybrid roles    Must
                          and why job titles      
                          alone are insufficient. 

  FR-047                  Aggregate competency    Should
                          patterns across         
                          analyzed vacancies.     

  FR-048                  Allow competency        Could
                          insights to be filtered 
                          by classification and   
                          other supported         
                          dimensions.             

  FR-049                  Display sample size and Should
                          dataset limitations     
                          alongside aggregated    
                          insights.               
  -----------------------------------------------------------------------

### 8.7 Career Fit Assessment

The assessment is included in the product scope. It is an exploratory
comparison tool, not a personality test, professional certification,
or prediction of hiring success.

  -----------------------------------------------------------------------
  ID                      Requirement             Priority
  ----------------------- ----------------------- -----------------------
  FR-050                  Allow users to describe  Must
                          relevant work, internship,
                          academic, volunteer, and
                          personal project experience.

  FR-051                  Allow users to identify  Must
                          competencies they have
                          demonstrated and provide
                          supporting examples or
                          evidence.

  FR-052                  Organize user-submitted  Must
                          experience and competencies
                          into a reviewable profile,
                          distinguishing user input
                          from AI interpretation.

  FR-053                  Compare the user's      Must
                          profile with requirements
                          extracted from available
                          104 vacancies.

  FR-054                  Explain matched,        Must
                          partially matched,      
                          missing, and unsupported
                          competencies, with links
                          to relevant job evidence.

  FR-055                  Clearly label results   Must
                          as exploratory and based
                          partly on user-submitted
                          information, not verified
                          ability or hiring predictions.

  FR-056                  Keep assessment data   Must
                          temporary for the current
                          session; do not create
                          persistent user profiles
                          or retain responses after
                          the session ends by default.
  -----------------------------------------------------------------------

### 8.8 AI assistant

  -----------------------------------------------------------------------
  ID                      Requirement             Priority
  ----------------------- ----------------------- -----------------------
  FR-057                  Provide an AI assistant Must
                          entry point for         
                          questions about the     
                          platform and PM/PjM     
                          careers.                

  FR-058                  When a user is viewing  Must
                          a vacancy, allow the    
                          assistant to use that   
                          vacancy's source and    
                          analysis data as        
                          context.                

  FR-059                  Allow general PM/PjM    Must
                          career questions when   
                          no vacancy is selected. 

  FR-060                  Make clear whether an   Must
                          answer is based on a
                          selected vacancy or     
                          general knowledge.      

  FR-061                  Update the assistant's  Must
                          vacancy context when
                          the user changes the
                          selected vacancy.

  FR-062                  Provide complete       Must
                          English and Traditional
                          Chinese interface
                          translations across
                          all pages and states.

  FR-063                  Provide a working      Must
                          light/dark theme switch
                          and retain the selected
                          theme during navigation.

  FR-064                  Adapt layouts and      Must
                          interactions to mobile,
                          tablet, laptop, desktop,
                          and large-screen widths.

  FR-065                  Keep core workflows    Must
                          usable at supported
                          viewport sizes without
                          broken layout or
                          unnecessary horizontal
                          scrolling.
  -----------------------------------------------------------------------

## 10. AI Analysis Framework and Guardrails

### 9.1 Role classification

The AI must classify based on: - Main management object. - Central
responsibilities. - Expected outcomes and ultimate accountability. -
Evidence in the JD. - Whether meaningful PM and PjM responsibilities
coexist.

The AI must not rely only on job title or keyword frequency.

### 9.2 Competency extraction

The platform uses the KSA framework described in `TP PMCS PRD.md`:

-   **Knowledge:** Knowledge areas or subject-matter understanding.
-   **Skills:** Capabilities or learned abilities used to perform work.
-   **Attitudes:** Work-related attitudes or behavioral orientations.

For each competency, where the source supports it, store: - Competency
category. - Competency name. - Requirement level: Required, Preferred,
or Unclear. - Evidence type: Explicit or Inferred. - Supporting JD
excerpt. - Confidence or uncertainty information, if a defined method is
adopted.

**Important:** An inferred competency is not the same as an explicitly
stated employer requirement. The interface must label it clearly. The
system must not turn every responsibility into a competency or infer
requirements merely because they are common in PM/PjM roles.

### 9.3 AI behavior rules

1.  **Source priority:** Specific vacancy facts must come from the
    original source data.
2.  **No fabrication:** Do not invent salary, location, benefits,
    responsibilities, skills, or requirements.
3.  **Responsibility-based classification:** Do not classify from job
    title alone.
4.  **Preserve uncertainty:** Use Unclear or state that information
    cannot be confirmed when evidence is insufficient.
5.  **Separate original and derived data:** AI output must not overwrite
    source data.
6.  **Traceable evidence:** Classification and competency conclusions
    should point to supporting JD excerpts.
7.  **Separate general knowledge:** General career guidance must not be
    presented as a fact about a specific vacancy.
8.  **Respect category differences:** Cross-category comparisons must
    preserve meaningful differences.
9.  **No unsupported market claims:** Aggregated insights must disclose
    dataset scope and sample size.
10. **Explain assessment limits:** Self-reported assessment results must
    not be presented as verified ability or hiring probability.

### 9.4 Structured AI output

The final technical schema has not yet been selected. At minimum, an
analysis record should be able to store:

``` json
{
  "job_id": "source-specific-job-id",
  "classification": "PM | PjM | Hybrid | Unclear | Other",
  "classification_reason": "Explanation supported by JD evidence",
  "related_domain_tags": ["PM-related"],
  "summary": {
    "en": "Plain-language summary",
    "zh-TW": "繁體中文摘要"
  },
  "responsibilities": [
    {
      "text": "Responsibility description",
      "evidence": "Supporting JD excerpt"
    }
  ],
  "competencies": [
    {
      "category": "Knowledge | Skills | Attitudes",
      "name": "Competency name",
      "requirement_level": "Required | Preferred | Unclear",
      "evidence_type": "Explicit | Inferred",
      "evidence": "Supporting JD excerpt"
    }
  ],
  "analysis_date": "ISO-8601 date",
  "analysis_version": "version identifier"
}
```

This is a conceptual example, not a finalized API contract. The team
must define validation rules, allowed values, evidence handling, and
confidence representation before implementation.

### 9.5 Human review and quality controls

-   Preserve the original JD alongside AI results.
-   Allow Unclear classifications.
-   Record analysis date and model or prompt version.
-   Re-run analysis when a JD materially changes or the analysis
    framework changes.
-   Manually review a sample of AI outputs.
-   Evaluate classification agreement and competency-extraction quality
    against a human-reviewed sample.
-   Do not claim an accuracy rate without a defined evaluation dataset
    and method.

## 11. Data Requirements and Source Handling

### 10.1 Primary source

**104 Job Bank:** https://www.104.com.tw/

104 is the intended primary source for Taiwanese vacancies. The team
has indicated that it can obtain API access from 104, so the planned
integration is through the 104 API rather than unauthorized scraping.

Before implementation, the team must verify the actual API endpoint and
documentation, authentication method, available fields, usage
permissions, rate limits, and any restrictions on storing or displaying
job-description content. The PRD assumes an authorized API integration;
it does not assume that every desired field or operation is supported.

### 10.2 Minimum job data fields

Where available and permitted: - Internal job record ID. - Source
name. - Source-specific job ID. - Original job URL. - Original job
title. - Company name. - Location. - Industry. - Salary range and salary
period. - Employment type. - Experience and education requirements. -
Original JD text and original language. - Posting date. -
First-collected date. - Last-checked date. - Last-changed date, if
known. - Vacancy status and status-verification date.

Missing source fields must remain missing; they must not be filled by AI
guesses.

### 10.3 Data separation

**Source data** is the original information supplied by the source. It
should be stored without AI rewriting.

**AI-derived data** may include: - Scope-screening result. - Role
classification and related-domain tags. - Classification rationale and
evidence. - Job summary. - Extracted responsibilities and
competencies. - Comparison results. - Other clearly labelled AI
analysis.

The two data layers must remain separate.

**User assessment data:** Experience descriptions, competency examples,
and assessment outputs are temporary session data. The MVP does not
require user accounts or persistent career profiles. The interface
should tell users that their assessment is temporary and should not
promise long-term storage or retrieval.

### 10.4 Data lifecycle

Proposed workflow: 1. Import or retrieve records through an approved
method. 2. Validate and normalize source fields. 3. Deduplicate records
using source ID where available, then URL and cautious similarity
checks. 4. Determine whether records are within the platform's scope. 5.
Store original source data. 6. Run AI classification and analysis. 7.
Store AI-derived results separately. 8. Record collection and analysis
timestamps. 9. When updated source content is available, compare it with
the stored record and re-analyze material changes. 10. Mark a vacancy
expired only when the source or approved checking method verifies its
status.

A failed or incomplete synchronization must not erase the last
successful dataset or cause unverified vacancies to be marked expired.

### 10.5 Source scope and exclusivity

104 Job Bank API is the platform's only external job-data source for the
current product scope. The platform must not import vacancy records or
job-description content from other job boards, O*NET, ESCO, or other
external occupational datasets.

Competency names and categories may be normalized internally using the
platform's own controlled vocabulary, but such normalization must not
introduce external vacancy facts or replace the requirements actually
stated in a 104 job description.

The original 104 job description remains the primary evidence source
for vacancy-specific classification and competency analysis.

## 12. User Flows

### 11.1 Job discovery flow

1.  User opens the platform.
2.  User chooses keyword search, filters, or AI natural-language search.
3.  If natural-language search is used, the system parses the request
    into editable conditions and clarifies ambiguity where necessary.
4.  The system queries the available dataset.
5.  User reviews results and adjusts filters or sorting.
6.  User opens a detailed analysis or the original source vacancy.
7.  User may select multiple vacancies for comparison.

### 11.2 Multi-job comparison flow

1.  User selects multiple vacancies from the result list.
2.  The interface displays the selected count.
3.  User starts AI comparison.
4.  AI groups vacancies by their existing classification.
5.  AI compares vacancies within each group.
6.  AI provides a cross-category synthesis.
7.  The report links findings to the relevant original vacancies and
    identifies missing information.

### 11.3 Career exploration flow

1.  User reads the Career Guide.
2.  User explores real vacancies in Job Explorer.
3.  User reviews job analyses and competency evidence.
4.  User views aggregated competency patterns in Competency Insights.
5.  User enters relevant work, internship, academic, volunteer, or
    personal project experience and identifies competencies they have
    demonstrated, adding examples where possible.
6.  AI organizes the submitted information into a reviewable profile.
7.  AI compares the profile with competency and experience requirements
    extracted from available 104 vacancies.
8.  User reviews matched, partially matched, missing, and unsupported
    requirements, with explanations and links to the relevant vacancies.
9.  The assessment remains temporary for the current session.

### 11.4 AI assistant flow

If implemented: - User may ask general PM/PjM career questions. - While
viewing a vacancy, user may ask questions grounded in that vacancy's
source and analysis data. - The interface must indicate whether the
response uses vacancy context or general knowledge. - Context must
update when the selected vacancy changes.

## 13. User Interface and Experience Requirements

### 12.1 Responsive design

Support a continuous range of viewport sizes, including smartphones,
small and large tablets, laptops, desktop monitors, and large displays.
The design must adapt fluidly rather than target only a few fixed screen
sizes.

Requirements:
- Use responsive layouts and flexible sizing; do not assume one fixed
  screen width or orientation.
- Adapt navigation to available space (for example, a compact menu on
  narrow screens and full navigation on wider screens).
- Reflow cards, comparison panels, forms, charts, and data tables so
  essential information remains readable and usable.
- Where a wide data table cannot reasonably reflow, provide a deliberate
  contained horizontal-scroll region rather than causing the entire page
  to overflow.
- Keep controls touch-friendly on touch devices and usable with a mouse
  and keyboard.
- Avoid clipped text, overlapping controls, broken layouts, and
  unnecessary page-level horizontal scrolling.
- Ensure core search, job details, comparison, Career Fit Assessment,
  and AI assistant workflows remain usable on narrow and wide screens.

Suggested starting breakpoints, to be validated during implementation:
- Mobile: below 768 px.
- Tablet: 768--1023 px.
- Desktop: 1024 px and above.
These breakpoints are implementation guidance, not a limit on supported
screen sizes; layouts must also work between breakpoints and on unusually
narrow or wide viewports.

### 12.2 Light and dark themes

- Provide a clearly visible, working control to switch between light
  mode and dark mode.
- Apply the selected theme consistently across every page and component,
  including navigation, cards, charts, forms, tables, dialogs, menus,
  notifications, and the floating AI assistant.
- Maintain readable text, clear component boundaries, and sufficient
  contrast in both themes; do not simply invert colors without checking
  the result.
- Preserve the user's selected theme while navigating between pages.
- The implementation may use the device's system preference as the
  initial default, but users must be able to override it.
- Theme switching must not reset the current page, search filters,
  selected vacancies, or assessment progress.

### 12.3 Bilingual interface

Support two complete interface languages:
- English.
- Traditional Chinese (繁體中文).

Requirements:
- Provide a clearly visible language switch available throughout the
  website.
- Translate all user-facing interface content, including navigation,
  buttons, filters, labels, instructions, validation messages, errors,
  notifications, empty states, tooltips, charts, and system messages.
- Present AI-generated summaries, classification explanations,
  competency explanations, comparison results, assessment feedback, and
  assistant responses in the currently selected language.
- Preserve the original JD exactly in its source language; do not
  overwrite or silently translate the original source text.
- Allow users to view the original JD alongside its translated summary
  or analysis.
- Maintain consistent terminology for PM, PjM, KSA, and other technical
  terms in both languages.
- Changing language should preserve the current page, search query,
  filters, selected vacancies, and assessment progress wherever
  technically practical.
- The default language may follow the browser/device language when it
  is supported; users must be able to change it manually.

### 12.4 Accessibility and usability

- Use clear labels and readable text.
- Do not rely on color alone to communicate classification or status.
- Provide text explanations for charts.
- Make forms keyboard accessible.
- Explain unfamiliar PM/PjM and KSA terminology.

### 12.5 UI acceptance criteria

The bilingual, theme, and responsive requirements are complete only when
all of the following checks pass:

1. A user can switch every page between English and Traditional Chinese;
   no essential navigation item, button, form label, error, or system
   message remains unintentionally untranslated.
2. AI-generated content follows the selected interface language, while
   the original job title and JD remain available in their source form.
3. A user can switch between light and dark mode on any page, and the
   selected mode remains active while navigating through the website.
4. The interface is tested at representative narrow-mobile, wide-mobile,
   tablet, laptop, desktop, and large-monitor viewport sizes, including
   widths between the suggested breakpoints.
5. At supported sizes, users can complete the main workflows—search,
   open a job, inspect analysis, compare vacancies, complete the Career
   Fit Assessment, and use the floating assistant—without blocked
   controls, overlapping elements, clipped content, or page-level
   horizontal overflow.
6. Both themes and both languages are checked across the core pages and
   important UI states, not just the homepage.

## 14. Technical Architecture

### 14.1 Confirmed technology stack

The team's selected implementation direction is:

- **Frontend:** React.
- **Backend:** Python with FastAPI.
- **Database:** PostgreSQL. Supabase may be used as the managed PostgreSQL platform and/or for supporting backend services if the team adopts it for deployment.
- **AI provider:** OpenAI API.
- **Data source:** 104 Job Bank API only.
- **Background processing:** Scheduled and queued backend jobs for daily synchronization and batch AI analysis.

The exact hosting provider, deployment topology, and whether Supabase services beyond managed PostgreSQL will be used remain deployment decisions. The architecture must preserve the separation between frontend, backend, database, and external APIs.

### 14.2 System architecture overview

The system consists of the following components:

1. **React frontend:** Responsive bilingual interface, job search, filters, job details, comparison, competency insights, Career Fit Assessment, theme/language controls, and floating AI assistant.
2. **FastAPI backend:** Authenticated application endpoints, business logic, 104 API integration, OpenAI API integration, validation, search, and data access.
3. **PostgreSQL database:** Original 104 vacancy records, source metadata, AI analysis results, competency records, synchronization logs, and evaluation data.
4. **Background worker and scheduler:** Runs the daily 104 synchronization and queues newly created or materially changed vacancies for batch AI analysis.
5. **External services:** 104 Job Bank API for vacancy data and OpenAI API for AI processing.

The browser must communicate with the backend. It must never call 104 or OpenAI using secret credentials embedded in frontend code.

### 14.3 Data Sources and 104 API Integration

**104 Job Bank API is the sole external job-data source for the current product.** The team has confirmed that its API access permits searching and retrieving public vacancies, including job descriptions.

The implementation must use the authorized API documentation and agreement to determine exact endpoint paths, parameters, field names, authentication, pagination, rate limits, and permitted content handling. The PRD does not invent endpoint names or assume undocumented API behavior.

#### 14.3.1 Retrieval workflow

1. The backend obtains or refreshes authentication credentials using the method specified by 104.
2. The backend sends vacancy-search or retrieval requests using supported parameters.
3. The backend follows the API's documented pagination or continuation mechanism, where provided.
4. The response parser maps available source fields to the internal vacancy schema.
5. Each record passes validation and cleaning before it is stored or updated.
6. The system records the synchronization run, source identifiers, timestamps, and outcome.
7. New or materially changed records are added to the AI-analysis queue.

#### 14.3.2 Internal field mapping

The following is the proposed internal schema. Exact source-field names must be mapped from the 104 API documentation.

| Internal field | Description | Requirement |
|---|---|---|
| `job_id` | Internal primary key | Required |
| `source` | Fixed source identifier, `104` | Required |
| `source_job_id` | Original 104 vacancy identifier | Required where provided by API |
| `source_url` | Link to original vacancy | Required where provided by API |
| `job_title_original` | Original job title | Required where available |
| `company_name_original` | Original company name | Required where available |
| `job_description_original` | Original JD text and language | Required for full JD analysis |
| `location_original` | Original location value | Optional |
| `salary_original` | Original salary text/value | Optional |
| `salary_min` / `salary_max` | Parsed salary bounds | Optional; only when reliably parseable |
| `salary_period` | Salary period, such as monthly or annual | Optional |
| `experience_requirement` | Source-stated experience requirement | Optional |
| `education_requirement` | Source-stated education requirement | Optional |
| `skills_original` | Source-provided skill fields, if available | Optional |
| `posting_date` | Source posting date | Optional |
| `first_collected_at` | First successful collection timestamp | Required |
| `last_checked_at` | Most recent successful source check | Required |
| `source_updated_at` | Source update timestamp, if supplied | Optional |
| `vacancy_status` | Source-provided or verified status | Optional |

Original source values must be preserved separately from normalized values. Missing fields must remain null and must not be completed using AI guesses.

### 14.4 Data Cleaning and Validation

Data cleaning occurs after API response parsing and before records are stored or updated.

#### 14.4.1 Cleaning rules

| Data issue | Required handling |
|---|---|
| Missing values | Store as null; display a clear "Not provided" state where appropriate. Never invent values. |
| Duplicate vacancies | Match by 104 source job ID first; then use source URL and cautious similarity checks where an ID is unavailable. |
| Salary format differences | Preserve original salary text and normalize numeric minimum/maximum values, currency, and salary period only when reliably parseable. |
| Location variations | Preserve original location and create a normalized search/display value without losing the source value. |
| Company-name variations | Preserve the original company name; use a separate normalized value for search/grouping where appropriate. |
| Empty or insufficient JD | Retain the vacancy record if otherwise valid, but do not run full AI analysis when there is insufficient text. Mark the analysis as unavailable or incomplete. |
| Invalid or missing source URL | Flag the record; do not fabricate a URL. |
| Updated vacancy | Compare source values with the stored record and update changed fields while retaining the original collection/update history where practical. |
| Unexpected field type or malformed response | Reject or quarantine the affected record, log the validation issue, and continue processing other valid records where safe. |

#### 14.4.2 Data integrity principles

- Cleaning must not rewrite or change the meaning of the original job description.
- Original and normalized values must be stored separately when normalization changes representation.
- A failed record must not cause unrelated valid records to be discarded.
- Duplicate detection must avoid merging two genuinely different vacancies solely because their titles or descriptions are similar.
- AI-generated information must never be written into original source fields.

#### 14.4.3 Cleaning pipeline

**API response → Field/type validation → Missing-value handling → Format normalization → Duplicate detection → Integrity checks → Clean vacancy records.**

### 14.5 Data Transformation and Processing

Data transformation converts validated source records into structures used by search, analysis, comparison, and career-insight features.

#### 14.5.1 Stage A: Structured record transformation

- Map 104 response fields to the internal vacancy schema.
- Preserve original source values and create separate normalized values for searchable fields.
- Parse salary bounds, salary period, and location only when the source data supports reliable interpretation.
- Store source identifiers and timestamps to support updates and traceability.

#### 14.5.2 Stage B: AI analysis input preparation

- Select the original JD and relevant source fields for analysis.
- Remove technical transport artifacts or irrelevant markup without changing the JD's meaning.
- Apply input-length handling according to the selected OpenAI model's limits; if content must be divided into sections, preserve section context and combine results through a validated process.
- Record the source record version or content hash used for analysis so results can be associated with the correct JD version.

#### 14.5.3 Stage C: AI-derived structured output

OpenAI API analysis may produce:

- PM/PjM/Hybrid/Unclear/Other classification.
- Main management object and ultimate responsibility.
- Classification rationale and supporting JD excerpts.
- Plain-language JD summary.
- Extracted responsibilities and expected outcomes.
- Knowledge, Skills, and Attitudes (KSA) competencies.
- Required, preferred, explicit, inferred, and uncertain labels.
- Analysis status, model identifier, prompt/schema version, and processing timestamp.

The output must be validated against the expected schema before it is stored. Invalid or incomplete output must be flagged and must not silently appear as a completed analysis.

#### 14.5.4 Stage D: Aggregation and feature preparation

- Aggregate competency frequencies across eligible analyzed vacancies.
- Calculate PM/PjM category distributions using the current dataset and selected filters.
- Keep explicit JD-stated competencies separate from AI-inferred competencies in all counts and visualizations.
- Record the number of vacancies included, filter conditions, and data freshness for each insight.
- Prepare structured vacancy and competency data for search, comparison, and Career Fit Assessment.

### 14.6 API Key Integration, Security, and Request Handling

The system integrates with two external APIs, each for a distinct purpose.

#### 14.6.1 104 Job Bank API

- Purpose: Search and retrieve public vacancy records and job descriptions.
- Authentication: Use the exact mechanism specified by 104.
- Execution location: Backend only.
- Request behavior: Follow documented pagination, rate limits, and retry requirements.
- Data handling: Follow the access agreement for storing, processing, and displaying retrieved vacancy content.

#### 14.6.2 OpenAI API

- Purpose: JD summarization, role classification, competency extraction, natural-language search support, comparison synthesis, Career Fit Assessment, and assistant responses.
- Authentication: OpenAI API key stored on the backend.
- Execution location: Backend only.
- Output handling: Validate structured responses before persistence or display.
- Cost controls: Track token usage, request counts, estimated cost, and failures; configure sensible limits for batch and interactive workloads.

#### 14.6.3 Credential security

- Never expose API keys or access tokens in frontend code, browser storage, client-visible configuration, or public repositories.
- Store credentials in backend environment variables or a secure secret manager.
- Separate development and production credentials where practical.
- Restrict access to credentials to the backend components that require them.
- Do not include credentials in application logs or error messages.
- Rotate or revoke credentials according to provider guidance and when exposure is suspected.

#### 14.6.4 Rate limits and retries

The actual 104 rate limit must be taken from the provider's documentation or agreement. Until confirmed, use the previously agreed conservative safeguard of no more than one request per second, unless 104 specifies a lower limit. This is an internal proposed safeguard, not a statement of 104's official limit.

- Make the throttle configurable.
- Respect provider retry instructions and `Retry-After` headers when supplied.
- On HTTP 429 or temporary server errors, use exponential backoff with a maximum retry count.
- Do not retry permanent authentication or permission errors indefinitely.
- Use pagination and batching only as supported by the API.
- Log request outcome and timing without logging secrets or unnecessary personal data.

For OpenAI API requests, implement bounded retries for temporary failures, handle rate-limit responses, and monitor token usage and cost. Batch analysis must use queue controls so a large synchronization does not create uncontrolled concurrent requests.

### 14.7 Analytical Methods

The platform uses a combination of explicit decision rules, LLM-assisted structured extraction, and statistical aggregation. AI output is advisory and must remain traceable to source evidence.

#### 14.7.1 PM/PjM role classification

**Method:** Responsibility-based classification framework supported by OpenAI LLM interpretation.

The analysis evaluates:
1. Main management object.
2. Central responsibilities.
3. Expected outcomes.
4. Ultimate responsibility.
5. Supporting evidence from the JD.

Classification categories:

- **PM:** Primarily accountable for product value and product outcomes.
- **PjM:** Primarily accountable for project objectives and delivery.
- **Hybrid:** The JD provides meaningful evidence of responsibility for both product and project outcomes.
- **Unclear:** Available JD evidence is insufficient to determine the primary responsibility.
- **Other:** The position does not meaningfully fit the PM/PjM scope.

Keyword frequency alone must not determine the classification. The model must provide evidence excerpts and a rationale. The system should use the agreed classification definitions and output schema consistently.

#### 14.7.2 Competency extraction

**Method:** OpenAI LLM-based structured information extraction.

Extract competencies into Knowledge, Skills, and Attitudes (KSA) categories where supported by the JD. For each competency, store:

- Competency name.
- KSA category.
- Requirement type (Required, Preferred, or Unclear).
- Evidence type (Explicit or Inferred).
- Supporting JD excerpt.
- Confidence or uncertainty indicator, if supported by the chosen output schema.

Explicitly stated and inferred competencies must remain distinguishable.

#### 14.7.3 Competency frequency analysis

**Method:** Statistical aggregation over the analyzed 104 vacancy dataset.

For a competency:

`Competency Frequency (%) = (Number of eligible analyzed vacancies containing the competency / Number of eligible analyzed vacancies) × 100`

The system must:
- Calculate explicit and inferred competency frequencies separately.
- Support filters such as PM/PjM category and other available vacancy fields.
- Display sample size and relevant dataset freshness.
- Avoid presenting the dataset as a complete representation of the entire labor market.

#### 14.7.4 Career Fit Assessment

**Method:** Evidence-based comparison between a user's free-text experience narrative and competency requirements extracted from 104 vacancies.

The AI identifies evidence in the user's narrative and compares it with vacancy requirements. Results should use understandable categories such as Matched, Partially Matched, Not Demonstrated, and Insufficient Evidence.

"Not Demonstrated" must not be described as proof that the user lacks a competency. Each result should show the relevant user-provided evidence, the corresponding vacancy requirement, and the limitations of the comparison.

#### 14.7.5 Multi-job comparison

**Method:** Structured comparison of stored vacancy fields and AI-derived analysis, with LLM-assisted natural-language synthesis where useful.

Compare responsibilities, management object, expected outcomes, competencies, required/preferred qualifications, and salary/location information where available and comparable. AI-generated explanations must be grounded in the selected records and must not invent missing values.

### 14.8 Automated Evaluation and Quality Assurance

The team selects **automated evaluation tests using a manually labelled reference dataset**.

- Create a representative set of 104 vacancy JDs and have team reviewers manually label their PM/PjM category and relevant competency evidence.
- Store the reference labels separately from AI outputs.
- Build repeatable evaluation tests that compare AI results against the manually labelled reference set.
- Report classification accuracy and a confusion matrix for role classification.
- Evaluate competency extraction using precision and recall against manually labelled competency evidence.
- Evaluate evidence traceability by checking whether cited excerpts genuinely support the associated classification or competency.
- Record model, prompt, schema, and dataset versions for each evaluation run.
- Review important failure cases and update prompts, rules, or schemas before rerunning the evaluation.

Automated metrics do not replace the manually labelled reference set. The team must not claim an accuracy rate without reporting the dataset size, labelling method, and evaluation procedure. The reference set should be reviewed for ambiguous cases and inter-reviewer disagreements.

### 14.9 Background Processing and Daily Data Synchronization

The selected processing approach is **batch processing in the background after daily synchronization**.

Target workflow:

1. At 06:00 Asia/Taipei, the scheduler starts the 104 synchronization job.
2. The backend retrieves vacancies using the authorized API and its documented pagination/update mechanism.
3. Records pass validation, cleaning, deduplication, and change detection.
4. New or materially changed vacancies are placed in an AI-analysis queue.
5. Background workers process queued vacancies through OpenAI API under configured concurrency, rate, and cost controls.
6. Validated AI results are stored separately from original source data.
7. The synchronization run records its completion status and the last successful update timestamp.

The displayed "last updated" timestamp must represent the last successful data synchronization, not merely the scheduled start time. If a run fails, retain the previous successful timestamp and existing valid data. The system must show partial or failed processing status where relevant and must not imply that all AI analysis is complete when queued work remains.

### 14.10 Conceptual Data Entities

Core entities include:

- **jobs:** Original 104 vacancy fields, source ID, source URL, original JD, normalized search fields, dates, and status.
- **job_analyses:** Classification, rationale, evidence, summaries, responsibilities, model/version, schema version, status, and analysis date.
- **competencies:** Normalized competency labels, KSA category, and internal taxonomy metadata.
- **job_competencies:** Links between vacancies and extracted competencies, including explicit/inferred status, requirement type, and evidence.
- **sync_runs:** Start/end times, status, records retrieved/created/updated/skipped/failed, and last successful synchronization.
- **analysis_jobs:** Queue status, retry count, error category, and processing timestamps.
- **evaluation_cases:** Manually labelled reference examples and versioned expected outputs for automated evaluation.

Assessment responses remain temporary session data in the MVP and are not stored as persistent user profiles by default.

### 14.11 End-to-End Pipeline Summary

The accompanying SVG summarizes the technical sequence and its relationship to the interface:

1. **Data source:** Retrieve public vacancy records and job descriptions from the authorized 104 Job Bank API only.
2. **Cleaning and transformation:** Validate source fields, handle missing values, detect duplicates, normalize searchable fields while preserving originals, and prepare structured records and JD analysis inputs.
3. **API integration and persistence:** The FastAPI backend securely orchestrates 104 and OpenAI API requests, applies documented provider limits, and stores original records, normalized fields, AI outputs, and operational metadata in PostgreSQL.
4. **Analysis:** Background workers use OpenAI for responsibility-based PM/PjM classification, evidence-backed summaries, KSA competency extraction, aggregation, comparison support, and Career Fit Assessment. Structured outputs are validated before use.
5. **UI presentation:** The React frontend presents search and filters, job cards and details, explicit/inferred competency evidence, comparison, Career Guide, Competency Insights, Career Fit Assessment, and the contextual AI assistant. The interface supports Traditional Chinese and English, light and dark themes, and responsive layouts.

**Operational loop:** A scheduler initiates daily synchronization at 06:00 Asia/Taipei. New or materially changed records are queued for batch analysis. The last successful synchronization timestamp is updated only after a successful run; a failed run must not overwrite the previous successful timestamp.

**Important boundary:** The team has confirmed permission to search and retrieve public 104 vacancies and JDs. Persistent storage, OpenAI processing, and redistribution/display conditions must still comply with the specific 104 access agreement, as recorded in Section 18.

Assessment responses remain temporary session data in the MVP and are not stored as persistent user profiles by default.

## 15. Non-Functional Requirements

### 15.1 Performance

-   Main pages should load within a reasonable time for the expected
    project dataset.
-   Search and filters should return results without unnecessary
    full-page reloads where feasible.
-   Large lists and charts should remain usable on mobile.

### 15.2 Reliability

-   A failed data import or AI run must not erase the last successful
    data.
-   Record errors and timestamps.
-   Avoid duplicate records during retries.

### 15.3 Accuracy and transparency

-   Show source links and last-checked dates where available.
-   Preserve original JDs.
-   Label AI inferences and uncertain outputs.
-   Explain comparison and recommendation factors.
-   Avoid unsupported market-wide claims.

### 15.4 Privacy and security

-   Collect only necessary user assessment data.
-   Explain how assessment responses are used.
-   Do not expose one user's assessment to another.
-   Use secure transport and appropriate access controls if accounts are
    implemented.
-   Review third-party AI data handling before sending user or source
    data to a model.
-   Provide a way to clear an assessment session if feasible.

### 15.5 Maintainability

-   Keep data collection, AI analysis, search, comparison, assessment,
    and UI logic separate.
-   Version prompts and analysis schemas.
-   Make competency definitions maintainable without requiring a full
    frontend rewrite.

## 16. Success Metrics and Evaluation

Numeric targets should be set after the team establishes a baseline and
tests the prototype.

### 16.1 Data quality

-   Number of usable vacancies.
-   Percentage of records with a valid source URL.
-   Duplicate rate.
-   Percentage of records with complete core fields.
-   Percentage of records with a known last-checked date.

### 16.2 AI analysis quality

-   Automated PM/PjM classification evaluation against a manually labelled reference dataset, including accuracy and a confusion matrix.
-   Competency extraction precision and recall against manually labelled examples.
-   Percentage of extracted competencies with supporting evidence and the validity of cited JD excerpts.
-   Rate of uncertain or unsupported outputs.
-   Rate of material analysis errors identified during review.

### 16.3 User experience

-   Users able to find and open a vacancy.
-   Users able to understand the PM/PjM guide.
-   Users able to complete a multi-job comparison.
-   User feedback on summary clarity and comparison usefulness.
-   Assessment completion and usefulness, if assessment is implemented.

### 16.4 System operations

-   Successful versus failed imports or scheduled checks.
-   Time since last successful update.
-   Number of records successfully re-analyzed after material changes.

Do not claim accuracy, market coverage, or recommendation effectiveness
before evaluation.

## 17. MVP Scope and Development Phases

The team has confirmed that **all features defined as part of the
product scope must be functional for the course demonstration**. The
phases below are therefore an implementation sequence, not a way to
defer features to a non-working prototype.

### Phase 1 --- Data foundation and core job intelligence

-   Authorized 104 API integration for searching and retrieving public
    vacancies, including job descriptions. A permitted fallback dataset
    may be used temporarily only if the live API integration is
    unavailable during the course demonstration, with the source clearly
    disclosed.
-   Original JD and source URL preservation, subject to 104 permissions.
-   PM/PjM scope screening and five-category classification.
-   Evidence-backed classification rationale and faithful JD summaries.
-   Competency extraction with explicit/inferred labels and evidence.
-   Keyword search and supported filters.
-   Search results, job details, and direct source links.
-   PM/PjM Career Guide.
-   Bilingual responsive interface and light/dark themes.

### Phase 2 --- Discovery, comparison, and assistant

-   AI natural-language search and editable parsed conditions.
-   Multi-job selection and AI comparison, including within-category
    and cross-category synthesis.
-   Competency Insights with sample-size and dataset limitations.
-   Functional floating AI assistant with job-specific and general
    conversation modes.

### Phase 3 --- Career Fit Assessment

-   Temporary free-text experience input.
-   AI extraction and organization of demonstrated competencies.
-   Matching against requirements extracted from 104 vacancies.
-   Evidence-based explanations of matches, partial matches, gaps, and
    insufficient evidence.
-   Development-area suggestions.

### Phase 4 --- Data operations and monitoring

-   Scheduled daily synchronization at 06:00 Taiwan time.
-   Change detection and re-analysis of updated vacancies.
-   Display of the last successful update date and time.
-   Functional Agent Activity and operational monitoring view.

**Completion rule:** Every feature above must work end-to-end in the
course demonstration. A static screen, disabled control, hard-coded
sample response, or non-functional button does not count as a completed
feature. If the live 104 API integration is temporarily unavailable during the
course demonstration, the team may use a permitted dataset as a clearly
disclosed temporary data source, but the
search, analysis, comparison, assistant, assessment, and monitoring
workflows must still function.

## 18. Decisions and Remaining Questions

This section records the team's latest decisions and separates them
from details that still need technical verification.

### 18.1 Confirmed product decisions

1.  **All product features must be functional for the course demo.**
    The phases in Section 16 describe the order of implementation,
    not permission to leave later features as static mockups.

2.  **Career Fit Assessment and Floating AI Assistant are included.**
    Both must be working features in the demonstrated product.

3.  **Inferred competencies must be visible and clearly labelled.**
    The UI must distinguish:
    - Explicit competencies: stated directly in the original job
      description.
    - Inferred competencies: interpreted by AI from responsibilities
      or contextual evidence, but not directly stated as a requirement.

4.  **104 API access for public vacancy search is confirmed.** The team
    has permission to search and retrieve public job vacancies from 104,
    including their job descriptions. The implementation must use this
    authorized access. Exact endpoint behavior, authentication, available
    fields, and rate limits still need to be configured from the API
    documentation. Permission to retrieve content does not automatically
    establish permission for every form of long-term storage, OpenAI
    processing, or public redistribution; those downstream uses must be
    checked against the granted terms.

5.  **Daily data refresh is required.** Schedule synchronization for
    06:00 Asia/Taipei every morning, subject to the API's documented
    limits. Show users the date and time of the last successful update.

6.  **Career Fit Assessment information is temporary.** The initial
    product does not need user accounts or permanent user profiles.
    User-submitted experience and competency information is used for
    the current session and is not retained after the session ends by
    default.

7.  **Matching is based on demonstrated experience and competencies.**
    Users describe relevant experiences in their own words. AI compares
    the evidence in that description with requirements extracted from
    vacancies on 104 and explains the evidence behind each match or gap.

8.  **Experience input uses Option A: free text.** Users can enter a
    natural-language description covering their role, responsibilities,
    project/work context, outcomes, and competencies demonstrated.
    These details are combined in one narrative input rather than
    collected through separate mandatory fields.

9.  **The AI provider will be OpenAI API.** The implementation must
    account for API credentials, usage costs, rate limits, error
    handling, and data privacy.

10. **The comparison dimensions are sufficient as defined in the PRD.**
    The assessment should compare Knowledge, Skills, Attitudes, and
    relevant experience requirements where the vacancy provides them.

11. **The website must be bilingual.** Users can switch between English
    and Traditional Chinese (繁體中文). All user-facing UI and AI-generated
    explanations must follow the selected language, while original 104
    job titles and JDs remain preserved in their source language.

12. **The website must support light and dark modes.** Users can switch
    themes through a visible control, and their selected theme must
    remain consistent across pages and components.

13. **The website must be fully responsive.** Layouts and core workflows
    must adapt to smartphones, tablets, laptops, desktop monitors, and
    large displays, including widths between the suggested breakpoints.

### 18.2 Confirmed technical decisions

1. **Exclusive external job-data source:** The platform will use only the authorized 104 Job Bank API for external vacancy data. O*NET, ESCO, other job boards, and external occupational datasets are excluded from the current product scope.
2. **Data cleaning:** The team accepts the cleaning rules in Section 14.4, including missing-value handling, duplicate detection, format normalization, original-value preservation, and record-integrity checks.
3. **Technology stack:** The selected direction is React for the frontend, Python with FastAPI for the backend, and PostgreSQL for the database. Supabase may be used as the managed PostgreSQL platform and/or for supporting backend services; the exact hosting configuration remains to be selected.
4. **AI processing strategy:** Vacancies will be batch-processed in the background after daily synchronization. New or materially changed records enter a processing queue.
5. **AI evaluation strategy:** The team will build automated evaluation tests using a manually labelled reference dataset. Human-labelled examples provide expected results, and repeatable automated tests compare AI outputs against them.

### 18.3 Product behavior to implement

**Career Fit Assessment**
- Provide one free-text input area where users can describe relevant
  work, internship, academic, volunteer, or personal project experience.
- The same description should include what the user did, their role,
  responsibilities, outcomes, and competencies they believe they
  demonstrated; users do not need to complete a separate evidence form.
- AI should identify possible competency evidence from the narrative
  and show the text passages supporting its interpretation.
- Extract and normalize competencies from the user's experience.
- Compare the resulting profile with requirements in individual 104
  vacancies.
- Show matched, partially matched, missing, and not-enough-information
  results.
- Explain each result with both user-provided evidence and the relevant
  job-description requirement.
- Avoid presenting a single match percentage as an objective measure
  of employability. If a score is later introduced, its calculation
  must be transparent and validated.

**Floating AI Assistant**
- Provide a persistent floating entry point across the platform.
- Answer general PM/PjM career questions when no vacancy is selected.
- Use the currently viewed vacancy's source content and AI analysis
  when the user asks about that vacancy.
- Clearly identify whether an answer is based on the selected vacancy
  or general PM/PjM knowledge.
- Update its context when the user navigates to another vacancy.
- Do not invent information absent from the source JD.

**Temporary session handling**
- Do not require account creation for the assessment MVP.
- Keep assessment responses and generated profile in session-scoped
  state.
- Provide a clear notice that responses are temporary and may be lost
  when the session ends, the page is refreshed, or the browser is
  closed, depending on implementation.
- Do not store assessment responses in persistent user profiles unless
  the team later approves a separate account and consent design.

### 18.4 Remaining technical questions and implementation proposals

1.  **Implement against the confirmed 104 public-vacancy API access.**
    The team has confirmed permission to search and retrieve public
    vacancies, including job descriptions. The remaining technical task
    is to map the authorized endpoints, request parameters, response
    fields, pagination behavior, and error handling from the API
    documentation.

2.  **Confirm 104 content-use permissions.**
    Verify whether the team may store job records, process JD content
    through OpenAI API, display summaries or excerpts, and link users
    to the original vacancies.

3.  **Confirm 104 authentication method.**
    Authentication means how 104 verifies that our backend is allowed
    to call its API. Common methods include an API key or an OAuth
    access token. The team must follow the method specified by 104.
    Credentials must be stored securely on the backend and must never
    be exposed in browser-side code or a public repository.

4.  **Confirm 104 rate limits and request rules.**
    A rate limit is the maximum number of API requests allowed within
    a period, such as requests per second or per minute. The actual
    104 limit is not yet known and must come from its API documentation
    or provider agreement.

    **Proposed client-side safeguard until 104 confirms its limit:**
    - Make no more than one request per second (a maximum of 60 per
      minute) as an initial conservative throttle.
    - If 104 specifies a lower limit, the lower limit takes precedence.
    - Use pagination and batch processing where supported.
    - On HTTP 429 or temporary server errors, pause and retry with
      exponential backoff; do not repeatedly retry in a tight loop.
    - Keep the throttle configurable so it can be adjusted without
      rewriting the application.

    This is our proposed safety setting, not a claim about 104's
    official rate limit.

5.  **Confirm daily synchronization behavior.**
    The target schedule is 06:00 Asia/Taipei. Confirm whether the API
    supports incremental retrieval of new or changed vacancies. If it
    does not, determine a permitted full-refresh strategy.

6.  **Confirm OpenAI API budget and model selection.**
    The provider is confirmed as OpenAI API, but the specific model,
    expected usage, and spending limit still need to be selected.
    The system should use backend-held credentials, usage monitoring,
    and sensible per-session limits.

7.  **Confirm the course-demo acceptance checklist.**
    All product features must work. The team should define test cases
    for job search, classification, JD analysis, competency labels,
    comparison, Career Fit Assessment, floating assistant, daily data
    update status, and Agent Activity before the final demonstration.

## 19. Key Risks and Mitigations

  -----------------------------------------------------------------------
  Risk                    Potential impact        Mitigation
  ----------------------- ----------------------- -----------------------
  104 API availability   Data synchronization    Verify authorized API
  or service disruption  may be delayed           behavior, retain the
                                                  last successful dataset,
                                                  and show sync status

  Inconsistent job titles Incorrect               Use
  and JDs                 classification          responsibility-based
                                                  rules, evidence, and an
                                                  Unclear category

  Ambiguous distinction   Hybrid or incorrect     Classify by management
  between PM and PjM      labels                  object and ultimate
                                                  responsibility; define
                                                  Hybrid carefully

  Unsupported             Misleading job or       Require evidence, label
  AI-generated            career guidance         inference, and manually
  competencies                                    review samples

  Small or biased dataset Misleading competency   Show sample size, date
                          insights                range, filters, and
                                                  coverage limitations

  Self-assessment bias    Recommendations may not Label responses as
                          reflect actual ability  self-reported and allow
                                                  users to revise them

  Misleading match score  Users may treat it as   Explain criteria and
                          hiring probability      show strengths, gaps,
                                                  and missing data

  Data becomes outdated   Users may see           Show last-checked date
                          unavailable vacancies   and verify status
                                                  before marking expired

  AI API cost or rate     Feature limitations or  Estimate usage,
  limits                  unexpected costs        prioritize core
                                                  functions, and set
                                                  request limits

  Scope expansion         Core job-discovery      Deliver in phases and
                          experience may remain   protect the Phase 1
                          unfinished              scope
  -----------------------------------------------------------------------

## 20. Product Summary

The platform brings together PM/PjM career guidance, job discovery,
AI-powered JD analysis, evidence-backed comparison, competency insights,
and optional career-fit reflection.

**User journey:**

**Understand PM and PjM → Explore real vacancies → Understand
responsibilities and requirements → Compare opportunities → Discover
competency patterns → Reflect on personal interests and competencies.**

**System workflow:**

**Approved job data → Data validation and deduplication → Original data
storage → AI classification and JD analysis → Search and comparison →
Competency insights → Optional career-fit assessment.**

**Product promise:**

**From Job Descriptions to Career Clarity.**
