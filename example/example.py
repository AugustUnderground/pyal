import yal

modules = yal.read('./example/example.yal')

participants = yal.util.as_participants(modules)
