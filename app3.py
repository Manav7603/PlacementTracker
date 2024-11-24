import streamlit as st
import pandas as pd
import plotly.express as px

# Confidentiality Disclaimer
# Confidentiality Disclaimer
if "disclaimer_shown" not in st.session_state:
    st.session_state["disclaimer_shown"] = False

if not st.session_state["disclaimer_shown"]:
    st.warning("""
    **Confidential Data Disclaimer**  
    This website contains sensitive and confidential data. Unauthorized access, sharing, or use of this information is strictly prohibited.  
    By proceeding, you agree to maintain the confidentiality of this information.
    """)
    proceed = st.button("Proceed")
    if proceed:
        st.session_state["disclaimer_shown"] = True
        st.rerun()  # Updated from st.experimental_rerun to st.rerun
    else:
        st.stop()


# Load datasets
jobs_file_path = "all_jobs_detailed_20241123_202726.csv"
placements_file_path = "Placements_CSE_2025_updated.xlsx"

# Load and process jobs data
jobs_data = pd.read_csv(jobs_file_path)
jobs_data.columns = jobs_data.columns.str.strip()
jobs_data["posting_date"] = pd.to_datetime(jobs_data["posting_date"], errors="coerce")
jobs_data = jobs_data.dropna(subset=["posting_date"])  # Drop rows with invalid dates

# Load and process placements data
placements_data = pd.read_excel(placements_file_path, sheet_name="Sheet1")
placements_data.columns = ["Company Name", "CTC (LPA)", "Students Placed", "Location", "Withdraw/Got PPO", "Bond Duration"]
placements_data = placements_data.dropna(subset=["Company Name"])
placements_data["CTC (LPA)"] = pd.to_numeric(placements_data["CTC (LPA)"], errors="coerce")
placements_data["Students Placed"] = pd.to_numeric(placements_data["Students Placed"], errors="coerce")
placements_data["Bond Duration"] = pd.to_numeric(placements_data["Bond Duration"], errors="coerce").fillna(0).astype(int)

# Sidebar navigation
st.sidebar.title("Nirma Placements & Jobs Tracker")
page = st.sidebar.radio("Navigate to:", [
    "Jobs Dashboard",
    "Placements Dashboard",
    "Integrated Insights",
    "Placement Trends",
    "Top Recruiters",
    "Industry Insights",
    "Location Heatmap",
    "Interactive Comparisons",
    "Student Opportunities",
    "Key Metrics",
    "Timeline Analysis",
    "Confidential Data Alert"
])

# Confidential Data Alert
if page == "Confidential Data Alert":
    st.title("⚠️ Confidential Data Disclaimer")
    st.warning("This website contains confidential placement and job data. Please handle this information with care.")

# Jobs Dashboard
elif page == "Jobs Dashboard":
    st.title("Jobs Dashboard")
    st.write("Explore the latest job postings.")
    st.dataframe(jobs_data)

    # Filters
    job_type_filter = st.multiselect("Filter by Job Type", options=jobs_data["job_type"].unique(), default=jobs_data["job_type"].unique())
    location_filter = st.multiselect("Filter by Location", options=jobs_data["location"].unique(), default=jobs_data["location"].unique())

    filtered_jobs = jobs_data[(jobs_data["job_type"].isin(job_type_filter)) & (jobs_data["location"].isin(location_filter))]
    st.write("Filtered Job Postings")
    st.dataframe(filtered_jobs)

    # Visualizations
    st.subheader("Job Types Distribution")
    job_type_fig = px.pie(filtered_jobs, names='job_type', title="Job Type Distribution")
    st.plotly_chart(job_type_fig)

    st.subheader("Jobs by Location")
    location_fig = px.bar(filtered_jobs, x='location', title="Job Postings by Location", color="job_type")
    st.plotly_chart(location_fig)

# Placements Dashboard
# elif page == "Placements Dashboard":
# Placements Dashboard
elif page == "Placements Dashboard":
    st.title("Placements Dashboard")
    st.write("Analyze placement statistics.")
    
    # Display raw data
    st.subheader("Placements Data")
    st.dataframe(placements_data)

    # Add filters for CTC and Bond Duration
    st.subheader("Filters")
    max_ctc = placements_data["CTC (LPA)"].max()
    max_bond = placements_data["Bond Duration"].max()

    if pd.isnull(max_ctc) or pd.isnull(max_bond):
        st.warning("Some data is missing or inconsistent. Please check the dataset.")
    else:
        # CTC Filter
        ctc_filter = st.slider(
            "Filter by CTC Range (LPA)",
            min_value=0.0,
            max_value=float(max_ctc),
            value=(0.0, float(max_ctc)),
            step=0.1
        )
        # Bond Filter
        bond_filter = st.slider(
            "Filter by Bond Duration (Months)",
            min_value=0,
            max_value=int(max_bond),
            value=(0, int(max_bond))
        )

        # Apply filters
        placements_data_filtered = placements_data[
            (placements_data["CTC (LPA)"] >= ctc_filter[0]) &
            (placements_data["CTC (LPA)"] <= ctc_filter[1]) &
            (placements_data["Bond Duration"] >= bond_filter[0]) &
            (placements_data["Bond Duration"] <= bond_filter[1])
        ]

        if placements_data_filtered.empty:
            st.warning("No placements data available for the selected filters.")
        else:
            # Display filtered data
            st.subheader("Filtered Placements Data")
            st.dataframe(placements_data_filtered)

            # Visualizations
            st.subheader("Visualizations")

            # Placement by Companies
            st.subheader("Students Placed per Company")
            company_fig = px.bar(
                placements_data_filtered,
                x='Company Name',
                y='Students Placed',
                title="Students Placed per Company",
                color="CTC (LPA)",
                labels={'Students Placed': "Number of Students"},
                height=400
            )
            st.plotly_chart(company_fig, use_container_width=True)

            # CTC Distribution
            st.subheader("CTC Distribution")
            ctc_fig = px.histogram(
                placements_data_filtered,
                x='CTC (LPA)',
                title="CTC Distribution",
                nbins=10,
                labels={'CTC (LPA)': "CTC in LPA"}
            )
            st.plotly_chart(ctc_fig, use_container_width=True)

            # Placements by Location
            st.subheader("Placements by Location")
            location_fig = px.bar(
                placements_data_filtered,
                x='Location',
                y='Students Placed',
                title="Placements by Location",
                color="Company Name",
                labels={'Students Placed': "Number of Students"},
                height=400
            )
            st.plotly_chart(location_fig, use_container_width=True)

            # Bond Duration Analysis
            st.subheader("Bond Duration Analysis")
            bond_fig = px.box(
                placements_data_filtered,
                x="Company Name",
                y="Bond Duration",
                color="Location",
                title="Bond Duration per Company",
                labels={'Bond Duration': "Bond Duration (Months)"},
                height=400
            )
            st.plotly_chart(bond_fig, use_container_width=True)

# Timeline Analysis
elif page == "Timeline Analysis":
    st.title("Timeline Analysis")
    st.write("Analyze when companies posted job openings.")

    # Clean jobs_data and ensure valid dates for timeline
    jobs_data = jobs_data.sort_values("posting_date")  # Sort by date
    timeline_fig = px.timeline(jobs_data, x_start="posting_date", x_end="posting_date", y="company_name", title="Company Job Posting Timeline")
    st.plotly_chart(timeline_fig)
    
   
# Integrated Insights
elif page == "Integrated Insights":
    st.title("Integrated Insights")
    st.write("Combined analysis of job postings and placements.")
    integrated_data = pd.merge(jobs_data, placements_data, left_on="company_name", right_on="Company Name", how="inner")
    st.dataframe(integrated_data)

    st.subheader("CTC vs Job Type")
    ctc_job_fig = px.scatter(integrated_data, x='CTC (LPA)', y='job_type', color='industry', title="CTC vs Job Type")
    st.plotly_chart(ctc_job_fig)
    
    st.subheader("Placements by Industry")
    industry_fig = px.bar(integrated_data, x="industry", y="Students Placed", color="job_type", title="Placements by Industry")
    st.plotly_chart(industry_fig)
    
    
    
# Placement Trends
elif page == "Placement Trends":
    st.title("Placement Trends")
    st.write("Analyze trends over time.")
    trend_fig = px.line(placements_data, x="Location", y="Students Placed", color="Company Name", title="Placement Trends by Location")
    st.plotly_chart(trend_fig)

# Top Recruiters
elif page == "Top Recruiters":
    st.title("Top Recruiters")
    top_recruiters = placements_data.groupby("Company Name")["Students Placed"].sum().sort_values(ascending=False).head(10)
    st.bar_chart(top_recruiters)
    
    
elif page == "Key Metrics":
    st.title("Key Metrics")
    total_jobs = len(jobs_data)
    total_placements = placements_data["Students Placed"].sum()
    average_ctc = placements_data["CTC (LPA)"].mean()
    average_bond = placements_data["Bond Duration"].mean()

    st.metric(label="Total Job Postings", value=total_jobs)
    st.metric(label="Total Students Placed", value=total_placements)
    st.metric(label="Average CTC (LPA)", value=f"{average_ctc:.2f}")
    st.metric(label="Average Bond Duration (Months)", value=f"{average_bond:.1f}")


# Industry Insights
elif page == "Industry Insights":
    st.title("Industry Insights")
    industry_fig = px.bar(jobs_data, x="industry", title="Industry Distribution of Job Postings")
    st.plotly_chart(industry_fig)

# Location Heatmap
elif page == "Location Heatmap":
    st.title("Location Heatmap")
    heatmap_data = placements_data.groupby("Location")["Students Placed"].sum().reset_index()
    heatmap_fig = px.choropleth(heatmap_data, locations="Location", locationmode="country names", color="Students Placed", title="Placement Heatmap by Location")
    st.plotly_chart(heatmap_fig)

# Interactive Comparisons
elif page == "Interactive Comparisons":
    st.title("Interactive Comparisons")
    st.write("Compare multiple metrics interactively.")
    comparison_metric = st.selectbox("Select Comparison Metric", ["CTC (LPA)", "Students Placed"])
    comparison_fig = px.box(placements_data, x="Company Name", y=comparison_metric, color="Location", title=f"{comparison_metric} Comparison")
    st.plotly_chart(comparison_fig)

# Student Opportunities
elif page == "Student Opportunities":
    st.title("Student Opportunities")
    st.write("Curated opportunities for students based on job postings and placements data.")
    opportunity_fig = px.treemap(jobs_data, path=["industry", "job_type", "location"], title="Job Opportunities Breakdown")
    st.plotly_chart(opportunity_fig)

# Timeline Analysis
elif page == "Timeline Analysis":
    st.title("Timeline Analysis")
    st.write("Analyze when companies posted job openings.")
    timeline_fig = px.timeline(jobs_data, x_start="posting_date", x_end="posting_date", y="company_name", title="Company Job Posting Timeline")
    st.plotly_chart(timeline_fig)
    
# Key Metrics
elif page == "Key Metrics":
    st.title("Key Metrics")
    total_jobs = len(jobs_data)
    total_placements = placements_data["Students Placed"].sum()
    average_ctc = placements_data["CTC (LPA)"].mean()
    average_bond = placements_data["Bond Duration"].mean()

    st.metric(label="Total Job Postings", value=total_jobs)
    st.metric(label="Total Students Placed", value=total_placements)
    st.metric(label="Average CTC (LPA)", value=f"{average_ctc:.2f}")
    st.metric(label="Average Bond Duration (Months)", value=f"{average_bond:.1f}")
# Export Options
st.sidebar.download_button("Download Jobs Data", jobs_data.to_csv(index=False), "jobs_data.csv", "text/csv")
st.sidebar.download_button("Download Placements Data", placements_data.to_csv(index=False), "placements_data.csv", "text/csv")
