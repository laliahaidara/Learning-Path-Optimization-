-- Checagem de volume (agregados apenas, nenhum dado pessoal)
SELECT 'courses' AS tabela, count(*) AS total FROM courses
UNION ALL SELECT 'course_modules', count(*) FROM course_modules
UNION ALL SELECT 'modules_com_workload', count(*) FROM course_modules WHERE workload_hours IS NOT NULL
UNION ALL SELECT 'course_topics', count(*) FROM course_topics
UNION ALL SELECT 'enrollments', count(*) FROM enrollments
UNION ALL SELECT 'module_progress', count(*) FROM user_module_progress
UNION ALL SELECT 'module_progress_concluidos', count(*) FROM user_module_progress WHERE completed_at IS NOT NULL AND started_at IS NOT NULL
UNION ALL SELECT 'course_feedback_com_nps', count(*) FROM course_feedback WHERE nps_score IS NOT NULL;
-- amostra do shape do workload_hours (só o json, sem título)
SELECT workload_hours FROM course_modules WHERE workload_hours IS NOT NULL LIMIT 3;
-- módulos por curso (distribuição do n das instâncias)
SELECT count(*) AS modulos_no_curso, count(*) OVER () AS total_cursos FROM course_modules GROUP BY course_id ORDER BY 1 DESC LIMIT 10;
