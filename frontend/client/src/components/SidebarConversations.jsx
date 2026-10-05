// Date-grouped conversation thread list
function groupConversationsByDate(conversations) {
  const groups = { Today: [], Yesterday: [], "Previous 7 Days": [], Older: [] };
  const now = new Date();
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  const yesterdayStart = todayStart - 86400000;
  const sevenDaysStart = todayStart - 86400000 * 6;

  conversations.forEach((conv) => {
    const time = new Date(conv.updatedAt || conv.createdAt).getTime();
    if (time >= todayStart) groups.Today.push(conv);
    else if (time >= yesterdayStart) groups.Yesterday.push(conv);
    else if (time >= sevenDaysStart) groups["Previous 7 Days"].push(conv);
    else groups.Older.push(conv);
  });

  return groups;
}

export default function SidebarConversations({
  conversations = [],
  activeConversationId,
  onSelectConversation,
  onNewChat,
  onDeleteConversation,
}) {
  const grouped = groupConversationsByDate(conversations);

  return (
    <div>
      <div className="panel-title">Chat Threads</div>
      <button className="new-chat-btn" onClick={onNewChat} type="button">
        <span>+</span> New Chat
      </button>

      <div className="conversations-section">
        {conversations.length === 0 ? (
          <div style={{ fontSize: "0.72rem", color: "var(--muted)", padding: "4px 2px" }}>No saved chats yet</div>
        ) : (
          Object.entries(grouped).map(([label, list]) => {
            if (list.length === 0) return null;
            return (
              <div key={label} className="date-group">
                <div className="date-group-label">{label}</div>
                {list.map((conv) => (
                  <div
                    key={conv._id}
                    className={`conversation-item ${activeConversationId === conv._id ? "active" : ""}`}
                    onClick={() => onSelectConversation(conv._id)}
                  >
                    <span className="conversation-title">{conv.title}</span>
                    <button
                      className="delete-conv-btn"
                      onClick={(e) => { e.stopPropagation(); onDeleteConversation(conv._id); }}
                      title="Delete Chat"
                      type="button"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
