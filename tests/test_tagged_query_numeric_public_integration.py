from atcodertools.client.models.problem_content import ProblemContent
from atcodertools.client.models.sample import Sample
from atcodertools.fmtprediction.predict_format import predict_format


def test_abc416_e_numeric_tagged_query_through_predict_format():
    content = ProblemContent(
        input_format_text=('N M\n'
 'A_1 B_1 C_1\n'
 '\\vdots\n'
 'A_M B_M C_M\n'
 'K T\n'
 'D_1 \\dots D_K\n'
 'Q\n'
 '\\mathrm{Query}_1\n'
 '\\vdots\n'
 '\\mathrm{Query}_Q\n'),
        samples=[
            Sample('4 1\n1 2 10\n2 100\n1 3\n5\n3\n1 2 3 60\n3\n2 4\n3\n', '440\n280\n900\n'),
        ],
    )
    content.input_format_blocks = ['N M\n'
 'A_1 B_1 C_1\n'
 '\\vdots\n'
 'A_M B_M C_M\n'
 'K T\n'
 'D_1 \\dots D_K\n'
 'Q\n'
 '\\mathrm{Query}_1\n'
 '\\vdots\n'
 '\\mathrm{Query}_Q\n']

    result = predict_format(content)

    assert str(result.format) == ('[TaggedQueryFormat: prefix=[(Singular: N),(Singular: M),(Parallel: A,B,C | 1 to '
 'M),(Singular: K),(Singular: T),(Parallel: D | 1 to K),(Singular: Q)], count=Q, '
 "variants=1:['int', 'int', 'int'],2:['int'],3:[]]")
