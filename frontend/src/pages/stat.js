import React from 'react';
import Sidebar from '../component/sidebar';
import SessionContext from '../context/SessionContext';
import ReactECharts from 'echarts-for-react';

class Stat extends React.Component {
    static contextType = SessionContext;

    constructor(props) {
        super(props);
        this.state = {
            stats: null,
            loading: true,
            error: null,
        };
    }

    async componentDidMount() {
        const sessionId = this.context;
        try {
            const result = await window.electronAPI.fetchUsageStats(sessionId);
            if (result.success) {
                this.setState({ stats: result.stats, loading: false });
            } else {
                this.setState({ error: result.error, loading: false });
            }
        } catch (err) {
            this.setState({ error: 'Failed to fetch stats', loading: false });
        }
    }

    getLikePieOption() {
        const { likedVideos, notLikedVideos } = this.state.stats;
        return {
            title: { text: 'Liked vs Not Liked Videos', left: 'center' },
            tooltip: { trigger: 'item' },
            series: [
                {
                    type: 'pie',
                    radius: '50%',
                    data: [
                        { value: likedVideos, name: 'Liked' },
                        { value: notLikedVideos, name: 'Not Liked' },
                    ],
                },
            ],
        };
    }

    getKeywordBarOption() {
        const data = this.state.stats.videosByKeyword || [];
        return {
            title: { text: 'Videos Watched Per Keyword' },
            tooltip: {},
            xAxis: {
                type: 'category',
                data: data.map(item => item.keyword),
                axisLabel: {
                    rotate: 45,
                    fontSize: 10,
                    overflow: 'truncate'
                }
            },
            yAxis: {
                type: 'value',
            },
            series: [
                {
                    type: 'bar',
                    data: data.map(item => item.count),
                },
            ],
        };
    }

    getDailyLineOption() {
        const data = this.state.stats.videosWatchedPerDay || [];
        return {
            title: { text: 'Videos Watched Per Day' },
            tooltip: { trigger: 'axis' },
            xAxis: {
                type: 'category',
                data: data.map(item => item.date).reverse(),
            },
            yAxis: {
                type: 'value',
            },
            series: [
                {
                    name: 'Watched',
                    type: 'line',
                    data: data.map(item => item.count).reverse(),
                },
            ],
        };
    }

    getPageLikesPerKeywordOption() {
        const raw = this.state.stats.keywordPageMap || [];

        const keywordLikeMap = {};
        raw.forEach(({ keyword, isLiked }) => {
            if (!keywordLikeMap[keyword]) keywordLikeMap[keyword] = 0;
            if (isLiked === 1) keywordLikeMap[keyword]++;
        });

        return {
            title: { text: 'Pages Liked Per Keyword' },
            tooltip: {},
            xAxis: {
                type: 'category',
                data: Object.keys(keywordLikeMap),
                axisLabel: {
                    rotate: 45,
                    fontSize: 10,
                    overflow: 'truncate'
                }
            },
            yAxis: {
                type: 'value',
            },
            series: [
                {
                    type: 'bar',
                    data: Object.values(keywordLikeMap),
                },
            ],
        };
    }

    getVideosPerPageOption() {
        const raw = this.state.stats.pageVideoMap || [];

        const pageCountMap = {};
        raw.forEach(({ pageUrl }) => {
            try {
                const pathParts = new URL(pageUrl).pathname.split('/').filter(Boolean);
                const username = pathParts[0] || pageUrl;
                if (!pageCountMap[username]) pageCountMap[username] = 0;
                pageCountMap[username]++;
            } catch {
                // fallback if URL parsing fails
                if (!pageCountMap[pageUrl]) pageCountMap[pageUrl] = 0;
                pageCountMap[pageUrl]++;
            }
        });

        const topPages = Object.entries(pageCountMap)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10); // Top 10 pages

        return {
            title: { text: 'Videos Watched Per Page (Top 10)' },
            tooltip: {},
            xAxis: {
                type: 'category',
                data: topPages.map(([username]) => username),
                axisLabel: {
                    rotate: 45,
                    fontSize: 10,
                    overflow: 'truncate'
                }
            },
            yAxis: {
                type: 'value',
            },
            series: [
                {
                    type: 'bar',
                    data: topPages.map(([, count]) => count),
                },
            ],
        };
    }

    getLikedPostsByKeywordOption() {
        const raw = this.state.stats.likedPostsByKeyword || [];

        const keywordCounts = {};
        raw.forEach(({ keyword }) => {
            if (!keywordCounts[keyword]) keywordCounts[keyword] = 0;
            keywordCounts[keyword]++;
        });

        const sorted = Object.entries(keywordCounts).sort((a, b) => b[1] - a[1]); // sort by count

        return {
            title: { text: 'Liked Posts per Keyword' },
            tooltip: {},
            xAxis: {
                type: 'value',
            },
            yAxis: {
                type: 'category',
                data: sorted.map(([keyword]) => keyword),
                axisLabel: {
                    fontSize: 10,
                    overflow: 'truncate',
                },
            },
            series: [
                {
                    type: 'bar',
                    data: sorted.map(([, count]) => count),
                },
            ],
        };
    }

    render() {
        const { loading, error, stats } = this.state;

        return (
            <div className="container mt-4" style={{ maxHeight: '100vh', overflowY: 'auto' }}>
                <div className="d-flex justify-content-between align-items-center mb-4">
                    <div className="d-flex align-items-center">
                        <Sidebar />
                        <h3 className="px-4">📊 MetaPriv: Usage Statistics</h3>
                    </div>
                </div>

                {loading && <p>Loading stats...</p>}
                {error && <div className="alert alert-danger">Error: {error}</div>}

                {stats && (
                    <div className="row">
                        <div className="col-md-6 mb-4">
                            <ReactECharts option={this.getLikePieOption()} />
                        </div>

                        <div className="col-md-6 mb-4">
                            <ReactECharts option={this.getKeywordBarOption()} />
                        </div>

                        <div className="col-md-12 mb-4">
                            <ReactECharts option={this.getDailyLineOption()} />
                        </div>

                        <div className="col-md-6 mb-4">
                            <ReactECharts option={this.getPageLikesPerKeywordOption()} />
                        </div>

                        <div className="col-md-6 mb-4">
                            <ReactECharts option={this.getVideosPerPageOption()} />
                        </div>

                        <div className="col-md-12 mb-4">
                            <ReactECharts option={this.getLikedPostsByKeywordOption()} />
                        </div>
                    </div>
                )}
            </div>
        );
    }
}

export default Stat;
