import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";


export type Locale = "en" | "ru" | "zh";

type Messages = {
  localeLabel: string;
  languages: Record<Locale, string>;
  hero: {
    eyebrow: string;
    title: string;
    copy: string;
    documents: string;
    selectedType: string;
  };
  selection: {
    eyebrow: string;
    emptyTitle: string;
    allDocsHint: string;
    docMeta: string;
    unknownLanguage: string;
    pages: string;
  };
  upload: {
    eyebrow: string;
    title: string;
    chooseFile: string;
    uploading: string;
    help: string;
  };
  library: {
    eyebrow: string;
    title: string;
    total: string;
    empty: string;
    language: string;
    pages: string;
    unknown: string;
    delete: string;
    deleting: string;
  };
  search: {
    eyebrow: string;
    title: string;
    queryLabel: string;
    placeholder: string;
    run: string;
    running: string;
    empty: string;
    allDocs: string;
    score: string;
    page: string;
    noPage: string;
  };
  qa: {
    eyebrow: string;
    title: string;
    questionLabel: string;
    placeholder: string;
    ask: string;
    asking: string;
    empty: string;
    allDocs: string;
    page: string;
    noPage: string;
  };
  summary: {
    eyebrow: string;
    title: string;
    short: string;
    detailed: string;
    generate: string;
    generating: string;
    empty: string;
  };
  status: Record<string, string>;
  misc: {
    loadingDocuments: string;
    docLabel: string;
    allDocuments: string;
  };
};

const messages: Record<Locale, Messages> = {
  en: {
    localeLabel: "Language",
    languages: { en: "EN", ru: "RU", zh: "中文" },
    hero: {
      eyebrow: "Document intelligence dashboard",
      title: "AI Document Analyst",
      copy: "Upload a source document, inspect its ingestion status, then move through retrieval, grounded Q&A, and summarization in one workspace.",
      documents: "Documents",
      selectedType: "Selected type",
    },
    selection: {
      eyebrow: "Selection",
      emptyTitle: "Choose a document",
      allDocsHint: "Search can run across all documents, while summaries require a selected document.",
      docMeta: "Doc",
      unknownLanguage: "Unknown language",
      pages: "pages",
    },
    upload: {
      eyebrow: "Ingestion",
      title: "Upload a document",
      chooseFile: "Choose a PDF or TXT file",
      uploading: "Uploading...",
      help: "Files are ingested immediately so search, QA, and summary are ready in one flow.",
    },
    library: {
      eyebrow: "Library",
      title: "Your documents",
      total: "total",
      empty: "No documents uploaded yet.",
      language: "Language",
      pages: "Pages",
      unknown: "Unknown",
      delete: "Delete",
      deleting: "Deleting...",
    },
    search: {
      eyebrow: "Retrieval",
      title: "Search across chunks",
      queryLabel: "Search query",
      placeholder: "Find clauses, names, or key passages",
      run: "Run search",
      running: "Searching...",
      empty: "Search results will appear here.",
      allDocs: "All docs",
      score: "Score",
      page: "Page",
      noPage: "No page",
    },
    qa: {
      eyebrow: "Question Answering",
      title: "Ask grounded questions",
      questionLabel: "Question",
      placeholder: "What does the agreement say about termination notice?",
      ask: "Ask",
      asking: "Asking...",
      empty: "Answers and supporting citations will appear here.",
      allDocs: "All docs",
      page: "Page",
      noPage: "No page",
    },
    summary: {
      eyebrow: "Summarization",
      title: "Generate a concise overview",
      short: "Short",
      detailed: "Detailed",
      generate: "Generate summary",
      generating: "Summarizing...",
      empty: "Select a document to generate a summary.",
    },
    status: {
      uploaded: "Uploaded",
      processing: "Processing",
      ready: "Ready",
      failed: "Failed",
    },
    misc: {
      loadingDocuments: "Loading documents...",
      docLabel: "Doc",
      allDocuments: "All docs",
    },
  },
  ru: {
    localeLabel: "Язык",
    languages: { en: "EN", ru: "RU", zh: "中文" },
    hero: {
      eyebrow: "Панель документной аналитики",
      title: "AI Document Analyst",
      copy: "Загружайте документы, проверяйте статус обработки, затем переходите к поиску, grounded Q&A и summary в одном рабочем пространстве.",
      documents: "Документы",
      selectedType: "Тип выбора",
    },
    selection: {
      eyebrow: "Выбор",
      emptyTitle: "Выберите документ",
      allDocsHint: "Поиск может работать по всем документам, а summary требует выбранный документ.",
      docMeta: "Документ",
      unknownLanguage: "Неизвестный язык",
      pages: "стр.",
    },
    upload: {
      eyebrow: "Загрузка",
      title: "Загрузить документ",
      chooseFile: "Выберите PDF или TXT файл",
      uploading: "Загрузка...",
      help: "Документы обрабатываются сразу, поэтому поиск, QA и summary доступны в одном потоке.",
    },
    library: {
      eyebrow: "Библиотека",
      title: "Ваши документы",
      total: "всего",
      empty: "Документы ещё не загружены.",
      language: "Язык",
      pages: "Страницы",
      unknown: "Неизвестно",
      delete: "Удалить",
      deleting: "Удаление...",
    },
    search: {
      eyebrow: "Поиск",
      title: "Поиск по чанкам",
      queryLabel: "Поисковый запрос",
      placeholder: "Найдите разделы, имена или ключевые фрагменты",
      run: "Запустить поиск",
      running: "Ищем...",
      empty: "Здесь появятся результаты поиска.",
      allDocs: "Все документы",
      score: "Скор",
      page: "Страница",
      noPage: "Без страницы",
    },
    qa: {
      eyebrow: "Вопрос-ответ",
      title: "Задавайте grounded вопросы",
      questionLabel: "Вопрос",
      placeholder: "Что документ говорит о сроке расторжения?",
      ask: "Спросить",
      asking: "Отвечаем...",
      empty: "Здесь появятся ответы и подтверждающие цитаты.",
      allDocs: "Все документы",
      page: "Страница",
      noPage: "Без страницы",
    },
    summary: {
      eyebrow: "Саммари",
      title: "Сгенерировать краткий обзор",
      short: "Короткое",
      detailed: "Подробное",
      generate: "Сделать summary",
      generating: "Суммаризируем...",
      empty: "Выберите документ, чтобы сделать summary.",
    },
    status: {
      uploaded: "Загружен",
      processing: "В обработке",
      ready: "Готов",
      failed: "Ошибка",
    },
    misc: {
      loadingDocuments: "Загружаем документы...",
      docLabel: "Док.",
      allDocuments: "Все документы",
    },
  },
  zh: {
    localeLabel: "语言",
    languages: { en: "EN", ru: "RU", zh: "中文" },
    hero: {
      eyebrow: "文档智能仪表盘",
      title: "AI Document Analyst",
      copy: "上传文档，查看处理状态，然后在同一工作区中完成检索、基于证据的问答和摘要。",
      documents: "文档数",
      selectedType: "当前类型",
    },
    selection: {
      eyebrow: "当前选择",
      emptyTitle: "请选择文档",
      allDocsHint: "搜索可以跨所有文档执行，而摘要需要先选择具体文档。",
      docMeta: "文档",
      unknownLanguage: "未知语言",
      pages: "页",
    },
    upload: {
      eyebrow: "导入",
      title: "上传文档",
      chooseFile: "选择 PDF 或 TXT 文件",
      uploading: "上传中...",
      help: "文件会立即进入处理流程，因此搜索、问答和摘要可以直接使用。",
    },
    library: {
      eyebrow: "文档库",
      title: "你的文档",
      total: "总计",
      empty: "还没有上传任何文档。",
      language: "语言",
      pages: "页数",
      unknown: "未知",
      delete: "删除",
      deleting: "删除中...",
    },
    search: {
      eyebrow: "检索",
      title: "跨分块搜索",
      queryLabel: "搜索问题",
      placeholder: "查找条款、名称或关键段落",
      run: "开始搜索",
      running: "搜索中...",
      empty: "搜索结果会显示在这里。",
      allDocs: "全部文档",
      score: "分数",
      page: "第",
      noPage: "无页码",
    },
    qa: {
      eyebrow: "问答",
      title: "提出有证据支撑的问题",
      questionLabel: "问题",
      placeholder: "协议中如何描述终止通知期？",
      ask: "提问",
      asking: "回答中...",
      empty: "答案和引用片段会显示在这里。",
      allDocs: "全部文档",
      page: "第",
      noPage: "无页码",
    },
    summary: {
      eyebrow: "摘要",
      title: "生成简明概览",
      short: "简短",
      detailed: "详细",
      generate: "生成摘要",
      generating: "摘要生成中...",
      empty: "请选择文档后再生成摘要。",
    },
    status: {
      uploaded: "已上传",
      processing: "处理中",
      ready: "已完成",
      failed: "失败",
    },
    misc: {
      loadingDocuments: "正在加载文档...",
      docLabel: "文档",
      allDocuments: "全部文档",
    },
  },
};

type I18nValue = {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  messages: Messages;
};

const I18nContext = createContext<I18nValue>({
  locale: "en",
  setLocale: () => undefined,
  messages: messages.en,
});

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocale] = useState<Locale>(() => {
    const stored =
      typeof window !== "undefined" && typeof window.localStorage?.getItem === "function"
        ? window.localStorage.getItem("ai-doc-analyst-locale")
        : null;
    if (stored === "ru" || stored === "zh" || stored === "en") {
      return stored;
    }
    return "en";
  });

  useEffect(() => {
    if (typeof window !== "undefined" && typeof window.localStorage?.setItem === "function") {
      window.localStorage.setItem("ai-doc-analyst-locale", locale);
    }
    document.documentElement.lang = locale;
  }, [locale]);

  const value = useMemo(
    () => ({
      locale,
      setLocale,
      messages: messages[locale],
    }),
    [locale],
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  return useContext(I18nContext);
}
