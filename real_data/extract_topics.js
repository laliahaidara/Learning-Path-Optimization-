// Extração nível-TÓPICO, agregada e anônima: índices, contagens e médias apenas.
const { Client } = require('pg');
(async () => {
  const c = new Client({ host: process.env.DB_HOST, user: process.env.DB_USERNAME,
    database: process.env.DB_NAME, password: process.env.DB_PASSWORD });
  await c.connect();
  const q = async (label, sql) => {
    const r = await c.query(sql);
    console.log('===' + label); console.log(JSON.stringify(r.rows));
  };
  await q('volumes', `SELECT 'activities' t, count(*)::int n FROM activities
    UNION ALL SELECT 'activity_attempts', count(*)::int FROM activity_attempts
    UNION ALL SELECT 'attempts_com_score', count(*)::int FROM activity_attempts WHERE score IS NOT NULL`);
  await q('topics', `
    WITH att AS (
      SELECT a.topic_id,
             count(*)::int AS n_attempts,
             round(avg(at2.score)::numeric, 3) AS score_medio,
             round(avg(CASE WHEN at2.correct THEN 1.0 ELSE 0.0 END)::numeric, 3) AS taxa_acerto
      FROM activity_attempts at2 JOIN activities a ON a.id = at2.activity_id
      GROUP BY a.topic_id),
    act AS (
      SELECT topic_id, count(*)::int AS n_activities,
             round(avg(difficulty)::numeric, 2) AS dificuldade_media
      FROM activities GROUP BY topic_id),
    prog AS (
      SELECT module_id,
             percentile_cont(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (completed_at - started_at))/60)
               FILTER (WHERE completed_at IS NOT NULL AND started_at IS NOT NULL) AS mediana_min
      FROM user_module_progress GROUP BY module_id),
    mt AS (SELECT module_id, count(*)::int AS topicos_no_modulo FROM course_topics GROUP BY module_id)
    SELECT dense_rank() OVER (ORDER BY cm.course_id) AS curso_idx,
           dense_rank() OVER (PARTITION BY cm.course_id ORDER BY cm."order", cm.id) AS modulo_idx,
           row_number() OVER (PARTITION BY ct.module_id ORDER BY ct."order", ct.id) AS topico_idx,
           mt.topicos_no_modulo,
           round(prog.mediana_min::numeric, 1) AS mediana_min_modulo,
           act.n_activities, act.dificuldade_media,
           att.n_attempts, att.score_medio, att.taxa_acerto
    FROM course_topics ct
    JOIN course_modules cm ON cm.id = ct.module_id
    JOIN mt ON mt.module_id = ct.module_id
    LEFT JOIN prog ON prog.module_id = cm.id
    LEFT JOIN act ON act.topic_id = ct.id
    LEFT JOIN att ON att.topic_id = ct.id
    ORDER BY curso_idx, modulo_idx, topico_idx`);
  await c.end();
})().catch(e => { console.error('ERRO:', e.message); process.exit(1); });
