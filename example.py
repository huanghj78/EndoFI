
class ExampleBreakpoint(gdb.Breakpoint):
    def __init__(self):
        super(ExampleBreakpoint, self).__init__(SQL_PARSER, gdb.BP_BREAKPOINT)

    def stop(self):
        # Obtain the current SQL statement 
        sql = gdb.parse_and_eval(PARSER_PARAM).string()
        if match(sql):
            return inject_fault()
        return False