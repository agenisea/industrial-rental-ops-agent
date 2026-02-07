interface FlaggedMessagesProps {
  messages: string[];
}

export function FlaggedMessages({ messages }: FlaggedMessagesProps) {
  if (messages.length === 0) return null;

  return (
    <div className="mt-1 space-y-0.5">
      <span className="font-bold">Flagged:</span>
      {messages.map((msg, i) => (
        <p key={i} className="pl-2 text-red-700">
          &ldquo;{msg}&rdquo;
        </p>
      ))}
    </div>
  );
}
