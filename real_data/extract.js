// Extração agregada e ANÔNIMA: índices no lugar de IDs/títulos, só números.
const { Client } = require('pg');
(async () => {
  const c = new Client({ host: process.env.DB_HOST, user: process.env.DB_USERNAME,
    database: process.env.DB_NAME, password: process.env.DB_PASSWORD });
  await c.connect();
  const q = async (label, sql) => {
    const r = await c.query(sql);
    console.log('===' + label); console.log(JSON.stringify(r.rows));
  };
  await q('modules', `
    WITH prog AS (
      SELECT module_id,
             count(*) FILTER (WHERE started_at IS NOT NULL)::int AS n_started,
             count(*) FILTER (WHERE completed_at IS NOT NULL)::int AS n_completed,
             percentile_cont(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (completed_at - started_at))/60)
               FILTER (WHERE completed_at IS NOT NULL AND started_at IS NOT NULL) AS mediana_min
      FROM user_module_progress GROUP BY module_id),
    nps AS (
      SELECT course_id, avg(nps_score)::numeric(4,2) AS nps_medio, count(*)::int AS n_nps
      FROM course_feedbacks WHERE nps_score IS NOT NULL GROUP BY course_id),
    tp AS (SELECT module_id, count(*)::int AS n_topics FROM course_topics GROUP BY module_id)
    SELECT dense_rank() OVER (ORDER BY cm.course_id) AS curso_idx,
           row_number() OVER (PARTITION BY cm.course_id ORDER BY cm."order") AS modulo_idx,
           cm."order" AS ordem,
           (SELECT avg(v::numeric)::numeric(5,2) FROM jsonb_each_text(cm.workload_hours) AS e(k,v)) AS workload_h_medio,
           tp.n_topics, prog.n_started, prog.n_completed,
           round(prog.mediana_min::numeric, 1) AS mediana_min_real,
           nps.nps_medio, nps.n_nps
    FROM course_modules cm
    LEFT JOIN prog ON prog.module_id = cm.id
    LEFT JOIN tp ON tp.module_id = cm.id
    LEFT JOIN nps ON nps.course_id = cm.course_id
    ORDER BY curso_idx, modulo_idx`);
  await q('activity_cols', `
    SELECT column_name, data_type FROM information_schema.columns
    WHERE table_name IN ('activity_attempts','activities') ORDER BY table_name, ordinal_position`);
  await c.end();
})().catch(e => { console.error('ERRO:', e.message); process.exit(1); });
