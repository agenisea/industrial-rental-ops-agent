interface RowProps {
  label: string;
  value: string;
}

export function Row({ label, value }: RowProps) {
  return (
    <div className="flex gap-1">
      <span className="font-bold shrink-0">{label}:</span>
      <span>{value}</span>
    </div>
  );
}
