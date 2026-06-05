document.addEventListener('DOMContentLoaded', () => {
    // Determine the latest timestamp so we know what to fetch
    const newsCards = document.querySelectorAll('.news-card');
    let latestTimestamp = null;
    
    if (newsCards.length > 0) {
        latestTimestamp = newsCards[0].getAttribute('data-timestamp');
    }

    const newsGrid = document.getElementById('newsGrid');

    // Only run polling if we are on the main news page
    if (newsGrid) {
        setInterval(() => {
            if (!latestTimestamp) return;

            fetch(`/api/news/latest?since=${latestTimestamp}`)
                .then(response => response.json())
                .then(data => {
                    if (data && data.length > 0) {
                        // Update latest timestamp to the newest article's time
                        latestTimestamp = data[0].created_at;

                        data.reverse().forEach(news => {
                            // Create news card element
                            const article = document.createElement('article');
                            article.className = 'news-card highlight-anim';
                            article.setAttribute('data-timestamp', news.created_at);

                            // Lang strings
                            const lang = window.CURRENT_LANG || 'ru';
                            let title = news[`title_${lang}`];
                            let content = news[`content_${lang}`];
                            
                            // Truncate content
                            if (content && content.length > 120) {
                                content = content.substring(0, 120) + '...';
                            }
                            
                            // Format date
                            const dateObj = new Date(news.created_at);
                            const tZDate = dateObj.getFullYear() + "-" + 
                                String(dateObj.getMonth() + 1).padStart(2, '0') + "-" + 
                                String(dateObj.getDate()).padStart(2, '0') + " " + 
                                String(dateObj.getHours()).padStart(2, '0') + ":" + 
                                String(dateObj.getMinutes()).padStart(2, '0');

                            let imageHtml = '';
                            if (news.image_filename) {
                                imageHtml = `
                                <div class="news-image">
                                    <img src="/static/images/uploads/${news.image_filename}" alt="News image">
                                </div>`;
                            } else {
                                imageHtml = `
                                <div class="news-image placeholder">
                                    <span>Жаңалықтар KZ</span>
                                </div>`;
                            }

                            // Build html
                            article.innerHTML = `
                                ${imageHtml}
                                <div class="news-content">
                                    <span class="news-category">${news.category_code}</span>
                                    <h3 class="news-title">${title}</h3>
                                    <p class="news-desc">${content}</p>
                                    <div class="news-meta">
                                        <span class="news-date">${tZDate}</span>
                                        <a href="/news/${news.id}" class="read-more">${window.READ_MORE_TEXT}</a>
                                    </div>
                                </div>
                            `;

                            // Remove no-news text if it exists
                            const noNews = document.querySelector('.no-news');
                            if (noNews) noNews.remove();

                            // Prepend to grid
                            newsGrid.prepend(article);
                        });
                    }
                })
                .catch(err => console.error("Error fetching latest news:", err));
        }, 30000); // 30 seconds
    }
});
