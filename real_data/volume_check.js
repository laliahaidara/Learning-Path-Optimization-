// Leitura agregada apenas — nenhum dado pessoal, nenhum texto livre.
const { Client } = require('pg');
(async () => {
  const c = new Client({
    host: process.env.DB_HOST, user: process.env.DB_USERNAME,
    database: process.env.DB_NAME, password: process.env.DB_PASSWORD,
  });
  await c.connect();
  const q = async (label, sql) => {
    const r = await c.query(sql);
    console.log('===', label); console.log(JSON.stringify(r.rows));
  };
  await q('volumes', `SELECT 'courses' t, count(*)::int n FROM courses
    UNION ALL SELECT 'course_modules', count(*)::int FROM course_modules
    UNION ALL SELECT 'modules_com_workload', count(*)::int FROM course_modules WHERE workload_hours IS NOT NULL
    UNION ALL SELECT 'course_topics', count(*)::int FROM course_topics
    UNION ALL SELECT 'enrollments', count(*)::int FROM enrollments
    UNION ALL SELECT 'module_progress', count(*)::int FROM user_module_progress
    UNION ALL SELECT 'progress_concluido', count(*)::int FROM user_module_progress WHERE completed_at IS NOT NULL AND started_at IS NOT NULL
    UNION ALL SELECT 'feedback_com_nps', count(*)::int FROM course_feedbacks WHERE nps_score IS NOT NULL`);
  await q('workload_shape', `SELECT workload_hours FROM course_modules WHERE workload_hours IS NOT NULL LIMIT 3`);
  await q('modulos_por_curso', `SELECT count(*)::int modulos FROM course_modules GROUP BY course_id ORDER BY 1 DESC LIMIT 15`);
  await c.end();
})().catch(e => { console.error('ERRO:', e.message); process.exit(1); });
