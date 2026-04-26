import { useI18n } from "../i18n";

type StatusBadgeProps = {
  status: string;
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const { messages } = useI18n();
  const normalizedStatus = status.toLowerCase();
  const label = messages.status[normalizedStatus] ?? status;

  return (
    <span className={`status-badge status-badge--${normalizedStatus}`}>
      {label}
    </span>
  );
}
