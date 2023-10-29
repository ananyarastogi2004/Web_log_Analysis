import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import adviz  # If you have a custom library for styling, make sure to import it

# Input your data
calculate_section = st.checkbox("Want to analyse your file? --- Currently not available")
if calculate_section:
    st.subheader("Input logfile")
    f = st.file_uploader("Choose a file")
    if f is not None:
        st.header("File uploaded successfully.")
        fpath = f
        df = pd.read_parquet(fpath)
    
        

# Create a Streamlit app
st.title("Web Server Log Analysis")

st.write('Analysis of file logs_final.parquet')
# Load your data
fpath = 'logs_final.parquet'
column = ['client', 'datetime', 'method', 'request', 'status', 'size', 'referer', 'user_agent', 'hostname', 'request_url','request_path', 'referer_url', 'referer_path', 'ua_family', 'ua_major', 'ua_os.family', 'ua_device.family', 'ua_device.model']
df = pd.read_parquet(fpath, columns=column)

st.write(df.head())

# Section 1: Top 10 hits hourly basis
calculate_section1 = st.checkbox("Calculate Top 10 Hits Hourly Basis")
if calculate_section1:
    st.header("Top 10 Hits Hourly Basis")
    df['hour'] = df['datetime'].dt.hour
    top_10_hours = df['hour'].value_counts().head(10)
    st.write(top_10_hours)

# Section 2: Count total number of HTTP codes
calculate_section2 = st.checkbox("Calculate Total Number of HTTP Codes")
if calculate_section2:
    st.header("Count Total Number of HTTP Codes")
    http_code_counts = df['status'].value_counts()
    st.write(http_code_counts)

# Section 3: Status codes
calculate_section3 = st.checkbox("Calculate Status Codes")
if calculate_section3:
    st.header("Status Codes")
    chart = adviz.status_codes(df['status'], theme='plotly_dark')
    st.plotly_chart(chart)

# Section 4: Page/resource size distributions
calculate_section4 = st.checkbox("Calculate Page/Resource Size Distributions")
if calculate_section4:
    st.header("Page/Resource Size Distributions - All Pages")
    size_df = df['size'].dropna()
    fig = px.histogram(
        size_df, x='size', title='Page Size Distribution (Bytes) - All Pages', template='plotly_dark')
    st.plotly_chart(fig)

    st.header("Page/Resource Size Distributions - Page Size < 100K")
    size_df_filtered = size_df[size_df.between(0, 100000)]
    fig_filtered = px.histogram(
        size_df_filtered, x='size', title='Page Size Distribution (Bytes) - Page Size < 100K', nbins=10, template='plotly_dark')
    st.plotly_chart(fig_filtered)

    st.header("Page/Resource Size Distributions - Page Size > 100K")
    size_df_filtered = size_df[size_df.between(100000, 99999999999999)]
    fig_filtered = px.histogram(
        size_df_filtered, x='size', title='Page Size Distribution (Bytes) - Page Size > 100K', nbins=10, template='plotly_dark')
    st.plotly_chart(fig_filtered)

# Section 5: Status codes by method
calculate_section5 = st.checkbox("Calculate Status Codes by Method")
if calculate_section5:
    st.header("Status Codes by Method")
    method_status_counts = (df[['method', 'status']]
                            .value_counts()
                            .reset_index()
                            .rename(columns={0: 'count'})
                            .sort_values(['method', 'count'], ascending=[True, False]))

    chart2 = adviz.style_table(
        method_status_counts,
        ['category', 'text', 'bar'],
        height=700,
        column_widths=[0.1, 0.1, 0.6],
        theme='plotly_dark',
        title='Status Codes by Method',
        font_size=16,
        width=800)
    st.plotly_chart(chart2)


# Section 6: Top User-agents/bots
calculate_section6 = st.checkbox("Calculate Top User-Agents/Bots")
if calculate_section6:
    st.header("Top User-Agents/Bots")
    top_bots = (df[df['ua_device.family'] == 'Spider']
                .groupby(['ua_family'])
                .agg({'size': ['count', 'sum']}))
    top_bots.columns = ['requests', 'bytes']
    top_bots['bytes per request'] = top_bots['bytes'] / top_bots['requests']
    top_bots = top_bots.sort_values(['requests'], ascending=False).reset_index().head(20).rename(columns={'ua_family': 'bot'})
    st.write(top_bots)

# Section 7: Requests and total bytes by User-agent/bot
calculate_section7 = st.checkbox("Calculate Requests and total bytes by User-agent/bot")
if calculate_section7:
    st.header("Requests and Total Bytes by User-Agent/Bot")
    top_bots = (df[df['ua_device.family'] == 'Spider']
                .groupby(['ua_family'])
                .agg({'size': ['count', 'sum']}))
    top_bots.columns = ['requests', 'bytes']
    top_bots = top_bots.sort_values('requests', ascending=False)
    top_bots['bytes per request'] = top_bots['bytes'] / top_bots['requests']
    st.write(top_bots.head(15).reset_index().rename(columns={'ua_family': 'bot'}))



# Section 9: Status code by bot
calculate_section9 = st.checkbox("Calculate Status code by bot")
if calculate_section9:
    st.header("Status Code by Bot")
    ua_status_counts = (df[(df['ua_device.family'] == 'Spider') & (df['ua_family'].isin(top_bots.head(9).index))]
                        .groupby(['ua_family', 'status'])['ua_device.family']
                        .count().reset_index()
                        .rename(columns={'ua_device.family': 'count'}))
    ua_status_counts = ua_status_counts[ua_status_counts['count'].ne(0)].reset_index(drop=True)
    ua_ranks = ua_status_counts.groupby('ua_family')['count'].sum().sort_values(ascending=False).reset_index().assign(rank=lambda df: range(1, len(df) + 1))[['ua_family', 'rank']]
    ua_status_counts = (pd.merge(ua_status_counts, ua_ranks).sort_values(['rank', 'status'], ascending=[True, True])[['ua_family', 'status', 'count']])
    chart3 = adviz.style_table(
        ua_status_counts.rename(columns={'ua_family': 'bot'}),
        ['category', 'text', 'bar'],
        column_widths=[0.3, 0.1, 0.5],
        font_size=17,
        theme='plotly_dark',
        title='Status Code Counts by User-Agent',
        precision=0,
        height=1100,
        width=900)
    st.plotly_chart(chart3)

# Section 10: Top pages/resources in bandwidth consumption
calculate_section10 = st.checkbox("Calculate Top pages/resources in bandwidth consumption")
if calculate_section10:
    st.header("Top Pages/Resources in Bandwidth Consumption")
    top_resources_bandwidth = (df[['request', 'request_dir_1', 'request_last_dir', 'size']]
                            .groupby('request')
                            .agg({'size': ['count', 'mean', 'sum']})
                            .sort_values(('size', 'sum'), ascending=False)
                            .head(40)).reset_index()
    top_resources_bandwidth.columns = ['uri', 'requests', 'avg. size', 'total bytes']
    st.write(top_resources_bandwidth)

# Section 11: Daily requests that resulted in 4xx or 5xx status codes
calculate_section11 = st.checkbox("Calculate Daily requests that resulted in 4xx or 5xx status codes")
if calculate_section11:
    st.header("Daily Requests with Status Code 4XX and 5XX")
    daily_requests = (df[['datetime', 'status']]
                    .assign(date=lambda df: df['datetime'].dt.date,
                            status_400=lambda df: df['status'].isin(['400', '401', '403', '404', '405', '406']),
                            status_500=lambda df: df['status'].isin(['500', '502', '503']))
                    .groupby('date').agg({'status_400': ['count', 'mean'], 'status_500': ['count', 'mean']}))
    daily_requests.columns = ['4XX Count','4XX Percentage', '5XX Count', '5XX Percentage']
    st.write(daily_requests)

# Section 12: Total hits per URL and URL with maximum hits
calculate_section12 = st.checkbox("Calculate Total hits per URL and URL with maximum hits")
if calculate_section12:
    st.header("Total Hits per URL")
    url_hit_counts = df['request'].value_counts()
    st.write(url_hit_counts)
    max_hits_url = url_hit_counts.idxmax()
    st.write(f'URL with maximum hits is: {max_hits_url}')

# Section 13: Total hits per platform
calculate_section13 = st.checkbox("Calculate Total hits per platform")
if calculate_section13:
    st.header("Total Hits per Platform")
    platform_hit_counts = df.groupby('ua_os.family')['client'].count()
    st.bar_chart(platform_hit_counts)

# Section 14: Total hits per browser
calculate_section14 = st.checkbox("Calculate Total hits per browser")
if calculate_section14:
    st.header("Total Hits per Browser")
    browser_hit_counts = df.groupby('ua_family')['client'].count()
    st.bar_chart(browser_hit_counts)
