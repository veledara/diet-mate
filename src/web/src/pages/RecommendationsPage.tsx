import React, { useEffect, useState } from "react";
import axios from "axios";
import { ClipLoader } from "react-spinners";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import { Components } from "react-markdown";

type ReportType = 'quality-report' | 'nutrition-report';

interface AIReport {
  report_id: string;
  report_type: ReportType;
  content: string;
  created_at: string;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const MarkdownComponents: Components = {
  a: ({ node, ...props }) => (
    <a
      style={{ color: "var(--primary-color)", textDecoration: "underline" }}
      {...props}
    />
  ),
  code: ({ node, className, children, ...props }) => (
    <code
      style={{
        backgroundColor: "rgba(255,255,255,0.1)",
        padding: "2px 4px",
        borderRadius: "4px",
        fontFamily: "monospace",
      }}
      {...props}
    >
      {children}
    </code>
  ),
  table: ({ node, ...props }) => (
    <div style={{ overflowX: "auto", width: "100%" }}>
      <table
        style={{
          borderCollapse: "collapse",
          margin: "1em 0",
          width: "100%"
        }}
        {...props}
      />
    </div>
  ),
  th: ({ node, ...props }) => (
    <th
      style={{
        padding: "6px 13px",
        border: "1px solid var(--divider-color)",
        backgroundColor: "var(--surface-color)",
      }}
      {...props}
    />
  ),
  td: ({ node, ...props }) => (
    <td
      style={{
        padding: "6px 13px",
        border: "1px solid var(--divider-color)",
      }}
      {...props}
    />
  ),
};

const RecommendationsPage: React.FC = () => {
  const [qualityReport, setQualityReport] = useState<AIReport | null>(null);
  const [nutritionReport, setNutritionReport] = useState<AIReport | null>(null);
  const [loading, setLoading] = useState({
    quality: false,
    nutrition: false,
    initial: true
  });
  const [error, setError] = useState("");

  const telegramUser = window.Telegram?.WebApp?.initDataUnsafe?.user;
  const telegramId = telegramUser?.id;

  useEffect(() => {
    const fetchInitialReports = async () => {
      if (!telegramId) {
        setError("Пользователь не авторизован.");
        return;
      }

      try {
        const [qualityRes, nutritionRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/api/v1/analytics/last-ai-report`, {
            params: {
              telegram_id: telegramId,
              report_type: 'quality-report'
            }
          }),
          axios.get(`${API_BASE_URL}/api/v1/analytics/last-ai-report`, {
            params: {
              telegram_id: telegramId,
              report_type: 'nutrition-report'
            }
          })
        ]);

        setQualityReport(qualityRes.data);
        setNutritionReport(nutritionRes.data);
      } catch (err) {
        if (axios.isAxiosError(err) && err.response?.status === 404) {
          setError("У вас пока нет отчетов. Нажмите на кнопку 'Сгенерировать новый отчет'");
        } else {
          setError("Проблема с отображением отчетов!");
        }
      } finally {
        setLoading(prev => ({ ...prev, initial: false }));
      }
    };

    fetchInitialReports();
  }, [telegramId]);

  const handleGenerateReport = async (reportType: ReportType) => {
    if (!telegramId) return;

    setLoading(prev => ({
      ...prev,
      [reportType === 'quality-report' ? 'quality' : 'nutrition']: true
    }));
    setError("");

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/v1/analytics/generate-ai-report`,
        {
          telegram_id: Number(telegramId),
          report_type: reportType,
          limit: 10
        },
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      reportType === 'quality-report'
        ? setQualityReport(response.data)
        : setNutritionReport(response.data);

    } catch (err) {
      let errorMessage = "Неизвестная ошибка";

      if (axios.isAxiosError(err)) {
        errorMessage = err.response?.data?.detail || err.message;
      } else if (err instanceof Error) {
        errorMessage = err.message;
      }

      setError(`Ошибка генерации отчёта: ${errorMessage}`);
    } finally {
      setLoading(prev => ({
        ...prev,
        [reportType === 'quality-report' ? 'quality' : 'nutrition']: false
      }));
    }
  };

  if (loading.initial) {
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

  return (
    <div style={{
      padding: "20px 15px 80px",
      color: "var(--text-primary)"
    }}>
      <h2 style={{
        marginBottom: "24px",
        textAlign: "center",
        color: "var(--text-primary)",
        fontSize: "1.5rem"
      }}>
        AI Рекомендации
      </h2>

      {error && (
        <div style={{
          backgroundColor: "var(--surface-color)",
          padding: "16px",
          borderRadius: "var(--border-radius)",
          marginBottom: "20px",
          color: "#ff4444"
        }}>
          {error}
        </div>
      )}

      {/* Блок анализа качества питания */}
      <div style={{
        backgroundColor: "var(--surface-color)",
        borderRadius: "var(--border-radius)",
        padding: "16px",
        marginBottom: "20px",
        boxShadow: "var(--shadow-md)"
      }}>
        <h3 style={{
          marginBottom: "12px",
          color: "var(--primary-color)"
        }}>
          Анализ качества питания
        </h3>

        <div style={{
          minHeight: "100px",
          marginBottom: "16px",
          overflowX: "auto",
          maxWidth: "100%",
          padding: "12px",
          backgroundColor: "var(--bg-color)",
          borderRadius: "8px"
        }}>
          {qualityReport?.content ? (
            <ReactMarkdown
              rehypePlugins={[rehypeRaw]}
              remarkPlugins={[remarkGfm]}
              components={MarkdownComponents}
            >
              {qualityReport.content}
            </ReactMarkdown>
          ) : "Отчет еще не сгенерирован"}
        </div>

        <button
          onClick={() => handleGenerateReport('quality-report')}
          disabled={loading.quality}
          style={{
            width: "100%",
            padding: "12px",
            backgroundColor: "var(--primary-color)",
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            gap: "8px",
            opacity: loading.quality ? 0.7 : 1,
            fontSize: "1.1rem"
          }}
        >
          {loading.quality ? (
            <ClipLoader color="#ffffff" size={18} />
          ) : (
            "Сгенерировать новый отчет"
          )}
          <span>🍎</span>
        </button>
      </div>

      {/* Блок анализа КБЖУ */}
      <div style={{
        backgroundColor: "var(--surface-color)",
        borderRadius: "var(--border-radius)",
        padding: "16px",
        marginBottom: "20px",
        boxShadow: "var(--shadow-md)"
      }}>
        <h3 style={{
          marginBottom: "12px",
          color: "var(--secondary-color)"
        }}>
          Анализ КБЖУ
        </h3>

        <div style={{
          minHeight: "100px",
          marginBottom: "16px",
          overflowX: "auto",
          maxWidth: "100%",
          padding: "12px",
          backgroundColor: "var(--bg-color)",
          borderRadius: "8px"
        }}>
          {nutritionReport?.content ? (
            <ReactMarkdown
              rehypePlugins={[rehypeRaw]}
              remarkPlugins={[remarkGfm]}
              components={MarkdownComponents}
            >
              {nutritionReport.content}
            </ReactMarkdown>
          ) : "Отчет еще не сгенерирован"}
        </div>

        <button
          onClick={() => handleGenerateReport('nutrition-report')}
          disabled={loading.nutrition}
          style={{
            width: "100%",
            padding: "12px",
            backgroundColor: "var(--secondary-color)",
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            gap: "8px",
            opacity: loading.nutrition ? 0.7 : 1,
            fontSize: "1.1rem"
          }}
        >
          {loading.nutrition ? (
            <ClipLoader color="#ffffff" size={18} />
          ) : (
            "Сгенерировать новый отчет"
          )}
          <span>📊</span>
        </button>
      </div>
    </div>
  );
};

export default RecommendationsPage;