#ifndef YYLTYPE
struct { int first_line; } yyltype;
#define YYLTYPE yyltype
#endif
#ifdef TEST_LEX
YYSTYPE yylval;
YYLTYPE yylloc;
#else
extern YYLTYPE yylloc;
#define YY_USER_INIT yylloc.first_line=1;
#endif
