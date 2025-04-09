import React, { useEffect, useState } from "react";
import axios from "axios";
import { ClipLoader } from "react-spinners";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  ReferenceLine,
  Legend
} from "recharts";

interface DayData {
  date: string;
  total_calories: number;
  total_proteins: number;
  total_fats: number;
  total_carbohydrates: number;
}

interface NutritionData {
  days: DayData[];
  user_nutrition: {
    calories: number;
    proteins: number;
    fats: number;
    carbohydrates: number;
  };
  average_calories: number;
  average_proteins: number;
  average_fats: number;
  average_carbohydrates: number;
}

interface WeightRecord {
  date: string;
  weight: number;
}

interface WeightHistory {
  records: WeightRecord[];
  target_weight: number;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const AnalyticsPage: React.FC = () => {
  const [nutritionData, setNutritionData] = useState<NutritionData | null>(null);
  const [weightHistory, setWeightHistory] = useState<WeightHistory | null>(null);
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
        const [nutritionRes, weightRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/api/v1/nutrition/periodic-summary`, {
            params: { telegram_id: telegramId, days: 7 }
          }),
          axios.get(`${API_BASE_URL}/api/v1/users/weight-history`, {
            params: { telegram_id: telegramId, limit: 15 }
          })
        ]);

        const sortedWeightRecords = weightRes.data.records.sort(
          (a: WeightRecord, b: WeightRecord) =>
            new Date(a.date).getTime() - new Date(b.date).getTime()
        );

        setNutritionData(nutritionRes.data);
        setWeightHistory({
          ...weightRes.data,
          records: sortedWeightRecords
        });
      } catch (err) {
        setError("Не получилось загрузить данные:(");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [telegramId]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("ru-RU", {
      day: "numeric",
      month: "short",
      hour: "2-digit",
      minute: "2-digit"
    }).replace(",", "");
  };

  const formatTooltipDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString("ru-RU", {
      day: "numeric",
      month: "long",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit"
    });
  };

  if (loading) {
    return (
      <div style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh"
      }}>
        <ClipLoader color="#7c3aed" size={35} />
      </div>
    );
  }

  if (error) {
    return (
      <div style={{
        padding: "20px",
        textAlign: "center",
        color: "#ff4444"
      }}>
        {error}
      </div>
    );
  }

  const calculateYDomain = (records: WeightRecord[], target: number) => {
    const values = records.map(r => r.weight);
    const min = Math.min(...values, target);
    const max = Math.max(...values, target);
    const padding = Math.max(2, (max - min) * 0.2);
    return [min - padding, max + padding];
  };

  return (
    <div style={{ padding: "20px 15px 80px", maxWidth: "800px", margin: "0 auto" }}>
      <h2 style={{
        marginBottom: "24px",
        textAlign: "center",
        color: "var(--text-primary)",
        fontSize: "1.5rem"
      }}>
        Аналитика
      </h2>

      {/* График питания за неделю */}
      <div style={{
        backgroundColor: "var(--surface-color)",
        borderRadius: "var(--border-radius)",
        padding: "16px",
        marginBottom: "20px"
      }}>
        <h3 style={{
          marginBottom: "16px",
          color: "var(--text-primary)",
        }}>
          Питание за неделю
        </h3>

        <div style={{ height: "300px" }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={nutritionData?.days}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tickFormatter={formatDate}
                tick={{ fill: "var(--text-secondary)" }}
              />
              <YAxis
                tick={{ fill: "var(--text-secondary)" }}
                domain={[0, (dataMax: number) => Math.round(dataMax * 1.2)]}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "var(--bg-color)",
                  border: "none",
                  borderRadius: "8px"
                }}
              />
              <Legend wrapperStyle={{ paddingTop: "20px" }} />

              {/* Столбцы */}
              <Bar
                dataKey="total_calories"
                name="Калории"
                fill="#FF6C9C"
                radius={[4, 4, 0, 0]}
              />
              <Bar
                dataKey="total_proteins"
                name="Белки (г)"
                fill="#67C8FF"
                radius={[4, 4, 0, 0]}
              />
              <Bar
                dataKey="total_fats"
                name="Жиры (г)"
                fill="#A586FF"
                radius={[4, 4, 0, 0]}
              />
              <Bar
                dataKey="total_carbohydrates"
                name="Углеводы (г)"
                fill="#6CFFA4"
                radius={[4, 4, 0, 0]}
              />

              {/* Линии норм */}
              <ReferenceLine
                y={nutritionData?.user_nutrition.calories}
                stroke="#FF6C9C"
                strokeDasharray="4 4"
                label={{
                  value: "Норма калорий",
                  fill: "#FF6C9C",
                  fontSize: 12,
                  position: "right"
                }}
              />
              <ReferenceLine
                y={nutritionData?.user_nutrition.proteins}
                stroke="#67C8FF"
                strokeDasharray="4 4"
                label={{
                  value: "Норма белков",
                  fill: "#67C8FF",
                  fontSize: 12,
                  position: "right"
                }}
              />
              <ReferenceLine
                y={nutritionData?.user_nutrition.fats}
                stroke="#A586FF"
                strokeDasharray="4 4"
                label={{
                  value: "Норма жиров",
                  fill: "#A586FF",
                  fontSize: 12,
                  position: "right"
                }}
              />
              <ReferenceLine
                y={nutritionData?.user_nutrition.carbohydrates}
                stroke="#6CFFA4"
                strokeDasharray="4 4"
                label={{
                  value: "Норма углеводов",
                  fill: "#6CFFA4",
                  fontSize: 12,
                  position: "right"
                }}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
          gap: "16px",
          marginTop: "20px",
          textAlign: "center"
        }}>
          <div>
            <div style={{ color: "var(--text-secondary)" }}>Средние калории</div>
            <div style={{ fontSize: "1.2em" }}>
              {nutritionData?.average_calories.toFixed(0)} / {nutritionData?.user_nutrition.calories.toFixed(0)}
            </div>
          </div>
          <div>
            <div style={{ color: "var(--text-secondary)" }}>Средние белки</div>
            <div style={{ fontSize: "1.2em" }}>
              {nutritionData?.average_proteins.toFixed(0)}g / {nutritionData?.user_nutrition.proteins.toFixed(0)}g
            </div>
          </div>
          <div>
            <div style={{ color: "var(--text-secondary)" }}>Средние жиры</div>
            <div style={{ fontSize: "1.2em" }}>
              {nutritionData?.average_fats.toFixed(0)}g / {nutritionData?.user_nutrition.fats.toFixed(0)}g
            </div>
          </div>
          <div>
            <div style={{ color: "var(--text-secondary)" }}>Средние углеводы</div>
            <div style={{ fontSize: "1.2em" }}>
              {nutritionData?.average_carbohydrates.toFixed(0)}g / {nutritionData?.user_nutrition.carbohydrates.toFixed(0)}g
            </div>
          </div>
        </div>
      </div>

      {/* График веса */}
      <div style={{
        backgroundColor: "var(--surface-color)",
        borderRadius: "var(--border-radius)",
        padding: "16px"
      }}>
        <h3 style={{
          marginBottom: "16px",
          color: "var(--text-primary)",
        }}>
          Динамика веса
        </h3>

        <div style={{ height: "250px" }}>
          {weightHistory && (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={weightHistory.records}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="date"
                  tickFormatter={formatDate}
                  tick={{ fill: "var(--text-secondary)" }}
                />
                <YAxis
                  tick={{ fill: "var(--text-secondary)" }}
                  domain={calculateYDomain(weightHistory.records, weightHistory.target_weight)}
                />
                <Tooltip
                  labelFormatter={formatTooltipDate}
                  formatter={(value: number) => [`${value} кг`, "Вес"]}
                  contentStyle={{
                    backgroundColor: "var(--bg-color)",
                    border: "none",
                    borderRadius: "8px"
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="weight"
                  stroke="#7c3aed"
                  strokeWidth={2}
                  dot={{ fill: "#7c3aed", strokeWidth: 2 }}
                />
                <ReferenceLine
                  y={weightHistory.target_weight}
                  label={{
                    value: `Цель: ${weightHistory.target_weight} кг`,
                    fill: "var(--text-primary)",
                    fontSize: 12,
                    position: "insideTopRight"
                  }}
                  stroke="#ff4444"
                  strokeWidth={1.5}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
};
export default AnalyticsPage;