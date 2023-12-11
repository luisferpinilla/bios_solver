from problema.problema import Problema

problema = Problema(file='model_template_1205v2.xlsm')

problema.solve(t_limit_minutes=10)

print('end')
