function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
}) {
  return (
    <div className="stat-card">

      <div className="stat-card-header">

        <span>
          {title}
        </span>

        {Icon && (
          <div className="stat-icon">
            <Icon size={20} />
          </div>
        )}

      </div>

      <strong className="stat-value">
        {value}
      </strong>

      {subtitle && (
        <div className="stat-subtitle">
          {subtitle}
        </div>
      )}

    </div>
  );
}

export default StatCard;