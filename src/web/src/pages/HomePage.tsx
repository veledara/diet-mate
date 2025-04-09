import React, { useEffect, useState } from "react";
import { Doughnut } from "react-chartjs-2";
import axios from "axios";
import {
    Chart as ChartJS,
    ArcElement,
    Tooltip,
    Legend,
    Title,
    AnimationSpec,
    Plugin
} from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend, Title);

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const centerLabelPlugin: Plugin<"doughnut"> = {
    id: "centerLabelPlugin",
    afterDraw: (chart) => {
        const { ctx, chartArea: { width, height } } = chart;
        const dataset = chart.data?.datasets?.[0]?.data as number[] || [];
        const meta = chart.getDatasetMeta(0);

        if (!dataset.length || !meta.data[0]) return;

        const consumed = dataset[0];
        const norm = (chart.config.options as any).userNorm || (dataset.length > 1 ? dataset[0] + dataset[1] : dataset[0]);

        let percentage = norm > 0 ? Math.round((consumed / norm) * 100) : 0;
        const text = `${percentage}%`;

        const textColor = percentage > 100 ? "#FF9E9E" : "#fff";

        ctx.save();
        ctx.fillStyle = textColor;
        ctx.font = "bold 20px sans-serif";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(text, width / 2, height / 2);
        ctx.restore();
    }
};

interface FoodLog {
    food_name: string;
    calories: number;
    proteins: number;
    fats: number;
    carbohydrates: number;
    date_added: string;
    rating: string;
}

interface DailySummary {
    total_calories: number;
    total_proteins: number;
    total_fats: number;
    total_carbohydrates: number;
    food_logs: FoodLog[];
    user_nutrition?: {
        calories: number;
        proteins: number;
        fats: number;
        carbohydrates: number;
    };
}

const HomePage: React.FC = () => {
    const [data, setData] = useState<DailySummary | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const telegramUser = window.Telegram?.WebApp?.initDataUnsafe?.user;
    const telegramId = telegramUser?.id;

    useEffect(() => {
        const fetchData = async () => {
            if (!telegramId) {
                setError("Пользователь не найден.");
                return;
            }
            try {
                const response = await axios.get(
                    `${API_BASE_URL}/api/v1/nutrition/daily-summary?telegram_id=${telegramUser.id}`
                );

                const sortedData = {
                    ...response.data,
                    food_logs: [...response.data.food_logs].sort((a, b) =>
                        new Date(b.date_added).getTime() - new Date(a.date_added).getTime()
                    )
                };

                setData(sortedData);
            } catch (err) {
                setError("Не получилось загрузить данные:(");
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const getChartData = (current: number, norm?: number, color?: string) => {
        const hasNorm = norm && norm > 0;
        const remainder = hasNorm ? Math.max(norm - current, 0) : 0;

        return {
            labels: [],
            datasets: [
                {
                    data: hasNorm ? [current, remainder] : [current],
                    backgroundColor: [color || "#4CAF50", "#37374A"],
                    borderWidth: 0,
                },
            ],
        };
    };

    const chartOptions = (_title: string, norm?: number) => ({
        plugins: {
            legend: { display: false },
            tooltip: { enabled: false },
        },
        animation: {
            duration: 2000,
            easing: "easeOutQuart" as AnimationSpec<"doughnut">["easing"],
        },
        cutout: "80%",
        responsive: true,
        maintainAspectRatio: false,
        userNorm: norm,
    });


    if (loading) {
        return <div style={{ padding: 80, textAlign: "center" }}>Загрузка...</div>;
    }
    if (error) {
        return <div style={{ padding: 80, textAlign: "center", color: "red" }}>{error}</div>;
    }
    if (!data) return null;

    return (
        <div style={{ padding: "20px 15px 80px" }}>
            <h2 style={{
                marginBottom: "24px",
                textAlign: "center",
                color: "var(--text-primary)",
                fontSize: "1.5rem"
            }}>
                Питание за сегодня
            </h2>

            <div style={{
                display: "flex",
                gap: "15px",
                justifyContent: "space-between",
                marginBottom: "30px",
                overflowX: "auto",
                padding: "10px 0"
            }}>
                {[
                    { title: "Калории", value: data.total_calories, norm: data.user_nutrition?.calories, color: "#FF6C9C" },
                    { title: "Белки", value: data.total_proteins, norm: data.user_nutrition?.proteins, color: "#67C8FF" },
                    { title: "Жиры", value: data.total_fats, norm: data.user_nutrition?.fats, color: "#A586FF" },
                    { title: "Углеводы", value: data.total_carbohydrates, norm: data.user_nutrition?.carbohydrates, color: "#6CFFA4" },
                ].map((item, index) => (
                    <div key={index} style={{
                        minWidth: "110px",
                        display: "flex",
                        flexDirection: "column",
                        alignItems: "center",
                        flexShrink: 0
                    }}>
                        <div style={{ width: "80px", height: "80px", marginBottom: "8px" }}>
                            <Doughnut
                                data={getChartData(item.value, item.norm, item.color)}
                                options={chartOptions(item.title, item.norm)}
                                plugins={[centerLabelPlugin]}
                            />
                        </div>
                        <div style={{ textAlign: "center" }}>
                            <div style={{ color: "#fff", fontSize: "0.9rem", fontWeight: 500 }}>
                                {item.title}
                            </div>
                            <div style={{ color: "rgba(255,255,255,0.7)", fontSize: "0.8rem" }}>
                                {item.value}
                                {item.norm ? `/${Math.round(item.norm)}` : ""}
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            <h3 style={{
                marginBottom: "16px",
                paddingLeft: "12px",
                color: "var(--text-primary)"
            }}>
                Приемы пищи:
            </h3>
            <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                {data.food_logs.map((meal, index) => (
                    <div
                        key={index}
                        style={{
                            padding: "16px",
                            borderRadius: "var(--border-radius)",
                            backgroundColor: "var(--surface-color)",
                            boxShadow: "var(--shadow-sm)",
                            transition: "all 0.3s ease"
                        }}
                    >
                        <div
                            style={{
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "center",
                                marginBottom: "8px",
                                color: "var(--text-secondary)"
                            }}
                        >
                            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                                <span style={{
                                    color: "rgba(255,255,255,0.7)",
                                    fontSize: "0.8em",
                                    whiteSpace: "nowrap"
                                }}>
                                    Ai-оценка:
                                </span>
                                <span style={{ fontSize: "1.2em" }}>{meal.rating}</span>
                                <span>
                                    {new Date(meal.date_added).toLocaleTimeString([], {
                                        hour: "2-digit",
                                        minute: "2-digit",
                                    })}
                                </span>
                            </div>
                            <div style={{
                                backgroundColor: "var(--bg-color)",
                                padding: "4px 8px",
                                borderRadius: "4px"
                            }}>
                                <span>{meal.calories} ккал</span>
                            </div>
                        </div>
                        <div
                            style={{
                                fontWeight: 500,
                                marginBottom: "8px",
                                color: "var(--text-primary)"
                            }}
                        >
                            {meal.food_name}
                        </div>
                        <div
                            style={{
                                display: "flex",
                                gap: "16px",
                                fontSize: "0.9em",
                                color: "var(--text-secondary)"
                            }}
                        >
                            <span>Б: {meal.proteins}г</span>
                            <span>Ж: {meal.fats}г</span>
                            <span>У: {meal.carbohydrates}г</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default HomePage;