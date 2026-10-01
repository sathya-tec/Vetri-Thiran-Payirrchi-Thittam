async function api(url, options = {}) {
    const response = await fetch(url, {
        credentials: "same-origin",
        ...options
    });

    let data = {};

    try {
        data = await response.json();
    } catch {
        data = {};
    }

    if (!response.ok) {
        throw new Error(
            data.detail || "Request failed"
        );
    }

    return data;
}


async function checkSession() {
    const response = await fetch(
        "/api/session-info",
        {
            credentials: "same-origin"
        }
    );

    if (response.status === 401) {
        return null;
    }

    if (!response.ok) {
        throw new Error("Unable to check session");
    }

    return await response.json();
}


async function updateAuthLink() {
    const link = document.getElementById("authLink");

    if (!link) {
        return;
    }

    try {
        const user = await checkSession();

        if (!user) {
            link.textContent = "Login";
            link.href = "/login";
            return;
        }

        link.textContent = "Logout";
        link.href = "#";

        link.onclick = async function (event) {
            event.preventDefault();

            try {
                await api(
                    "/api/logout",
                    {
                        method: "POST"
                    }
                );
            } finally {
                window.location.href = "/";
            }
        };

    } catch {
        link.textContent = "Login";
        link.href = "/login";
    }
}


document.addEventListener(
    "DOMContentLoaded",
    updateAuthLink
);


function setupAuthForm(id, url, redirect) {
    const form = document.getElementById(id);

    if (!form) {
        return;
    }

    form.addEventListener(
        "submit",
        async function (event) {
            event.preventDefault();

            const message = form.querySelector(".msg");

            if (message) {
                message.textContent = "";
            }

            const body = Object.fromEntries(
                new FormData(form).entries()
            );

            try {
                await api(
                    url,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify(body)
                    }
                );

                window.location.href = redirect;

            } catch (error) {
                if (message) {
                    message.textContent = error.message;
                }
            }
        }
    );
}


function setupRegister() {
    const form = document.getElementById("registerForm");

    if (!form) {
        return;
    }

    form.addEventListener(
        "submit",
        async function (event) {
            event.preventDefault();

            const message = form.querySelector(".msg");

            if (message) {
                message.textContent = "";
            }

            const body = Object.fromEntries(
                new FormData(form).entries()
            );

            try {
                await api(
                    "/api/register",
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify(body)
                    }
                );

                await api(
                    "/api/login",
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            email: body.email,
                            password: body.password
                        })
                    }
                );

                window.location.href = "/dashboard";

            } catch (error) {
                if (message) {
                    message.textContent = error.message;
                }
            }
        }
    );
}


function showResult(data) {
    const root = document.getElementById("result");

    if (!root) {
        return;
    }

    root.innerHTML = `
        <div class="result-card">

            <p class="eyebrow">
                AI RECOMMENDATIONS
            </p>

            <h2>
                ${escapeHtml(data.title)}
            </h2>

            <p>
                ${escapeHtml(data.summary)}
            </p>

            <p>
                <strong>Estimated spend:</strong>
                ₹${Number(data.budget_used || 0).toLocaleString("en-IN")}

                &nbsp;&nbsp;

                <strong>Remaining:</strong>
                ₹${Number(data.remaining_budget || 0).toLocaleString("en-IN")}
            </p>

            <h3>
                Budget allocation
            </h3>

            ${(data.allocations || []).map(
                allocation => `
                    <div class="allocation">

                        <span>
                            ${escapeHtml(allocation.category)}
                        </span>

                        <strong>
                            ₹${Number(
                                allocation.amount || 0
                            ).toLocaleString("en-IN")}
                        </strong>

                        <span>
                            ${escapeHtml(allocation.percentage)}%
                        </span>

                    </div>
                `
            ).join("")}

            <h3>
                Recommendations
            </h3>

            <div class="rec-grid">

                ${(data.recommendations || []).map(
                    recommendation => `
                        <article class="rec">

                            <b>
                                ${escapeHtml(
                                    recommendation.category
                                )}
                            </b>

                            <h3>
                                ${escapeHtml(
                                    recommendation.name
                                )}
                            </h3>

                            <div class="price">
                                ~₹${Number(
                                    recommendation.estimated_price || 0
                                ).toLocaleString("en-IN")}
                                ·
                                ${escapeHtml(
                                    recommendation.platform
                                )}
                            </div>

                            <p>
                                ${escapeHtml(
                                    recommendation.reason
                                )}
                            </p>

                            <a
                                target="_blank"
                                rel="noopener noreferrer"
                                href="${escapeAttr(
                                    recommendation.search_url
                                )}"
                            >
                                Search on
                                ${escapeHtml(
                                    recommendation.platform
                                )}
                                →
                            </a>

                        </article>
                    `
                ).join("")}

            </div>

            <h3>
                Cautions
            </h3>

            <ul>

                ${(data.cautions || []).map(
                    caution => `
                        <li>
                            ${escapeHtml(caution)}
                        </li>
                    `
                ).join("")}

            </ul>

        </div>
    `;
}


function setupJSONPlanner(id, url) {
    const form = document.getElementById(id);

    if (!form) {
        return;
    }

    form.addEventListener(
        "submit",
        async function (event) {
            event.preventDefault();

            const button = form.querySelector("button");

            if (button) {
                button.disabled = true;
                button.textContent = "Generating...";
            }

            try {
                const formData = new FormData(form);
                const body = {};

                for (const [key, value] of formData.entries()) {
                    if (key === "rooms") {
                        if (!body.rooms) {
                            body.rooms = [];
                        }

                        body.rooms.push(value);
                    } else {
                        body[key] = value;
                    }
                }

                if (url.includes("home")) {
                    body.budget = Number(body.budget);
                    body.rooms = body.rooms || [];
                }

                if (url.includes("party")) {
                    body.budget = Number(body.budget);
                    body.guests = Number(body.guests);
                }

                const result = await api(
                    url,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify(body)
                    }
                );

                showResult(result);

                const resultElement =
                    document.getElementById("result");

                if (resultElement) {
                    window.scrollTo({
                        top: resultElement.offsetTop - 80,
                        behavior: "smooth"
                    });
                }

            } catch (error) {
                const resultElement =
                    document.getElementById("result");

                if (resultElement) {
                    resultElement.innerHTML = `
                        <div class="result-card">
                            <p class="msg">
                                ${escapeHtml(error.message)}
                            </p>
                        </div>
                    `;
                }

            } finally {
                if (button) {
                    button.disabled = false;
                    button.textContent = "Generate plan";
                }
            }
        }
    );
}


function setupMultipartPlanner(id, url) {
    const form = document.getElementById(id);

    if (!form) {
        return;
    }

    form.addEventListener(
        "submit",
        async function (event) {
            event.preventDefault();

            const button = form.querySelector("button");

            if (button) {
                button.disabled = true;
                button.textContent = "Analyzing...";
            }

            try {
                const result = await api(
                    url,
                    {
                        method: "POST",
                        body: new FormData(form)
                    }
                );

                showResult(result);

                const resultElement =
                    document.getElementById("result");

                if (resultElement) {
                    window.scrollTo({
                        top: resultElement.offsetTop - 80,
                        behavior: "smooth"
                    });
                }

            } catch (error) {
                const resultElement =
                    document.getElementById("result");

                if (resultElement) {
                    resultElement.innerHTML = `
                        <div class="result-card">
                            <p class="msg">
                                ${escapeHtml(error.message)}
                            </p>
                        </div>
                    `;
                }

            } finally {
                if (button) {
                    button.disabled = false;
                    button.textContent =
                        "Generate jewelry plan";
                }
            }
        }
    );
}


async function loadDashboard() {
    try {
        const user = await api(
            "/api/session-info"
        );

        const userName =
            document.getElementById("userName");

        if (userName) {
            userName.textContent = user.name;
        }

        const history = await api(
            "/api/history"
        );

        const root =
            document.getElementById("recentPlans");

        if (!root) {
            return;
        }

        root.innerHTML =
            history
                .slice(0, 5)
                .map(
                    item => `
                        <div class="history-item">

                            <header>

                                <strong>
                                    ${escapeHtml(
                                        item.planner.toUpperCase()
                                    )}
                                </strong>

                                <span>
                                    ₹${Number(
                                        item.budget || 0
                                    ).toLocaleString("en-IN")}
                                </span>

                            </header>

                            <p>
                                ${new Date(
                                    item.created_at
                                ).toLocaleString()}
                            </p>

                        </div>
                    `
                )
                .join("")
            ||
            '<p class="loading">No plans yet.</p>';

    } catch {
        window.location.href = "/login";
    }
}


async function loadHistory() {
    try {
        const rows = await api(
            "/api/history"
        );

        const root =
            document.getElementById("historyList");

        if (!root) {
            return;
        }

        root.innerHTML =
            rows
                .map(
                    item => `
                        <article class="history-item">

                            <header>

                                <strong>
                                    ${escapeHtml(
                                        item.planner.toUpperCase()
                                    )}
                                    PLAN
                                </strong>

                                <span>
                                    ₹${Number(
                                        item.budget || 0
                                    ).toLocaleString("en-IN")}
                                </span>

                            </header>

                            <p>
                                ${new Date(
                                    item.created_at
                                ).toLocaleString()}
                            </p>

                            <p>
                                ${escapeHtml(
                                    item.result?.summary || ""
                                )}
                            </p>

                        </article>
                    `
                )
                .join("")
            ||
            '<p class="loading">No saved recommendations yet.</p>';

    } catch {
        window.location.href = "/login";
    }
}


function escapeHtml(value) {
    return String(
        value ?? ""
    ).replace(
        /[&<>'"]/g,
        character => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            "'": "&#39;",
            '"': "&quot;"
        })[character]
    );
}


function escapeAttr(value) {
    return escapeHtml(value);
}