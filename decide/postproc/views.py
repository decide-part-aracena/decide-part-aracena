from rest_framework.views import APIView
from rest_framework.response import Response
import collections


class PostProcView(APIView):

    def identity(self, options):
        out = []

        for opt in options:
            out.append({
                **opt,
                'postproc': opt['votes'],
            });

        out.sort(key=lambda x: -x['postproc'])
        return Response(out)
    
    def dhont_method(self, options, seats):

        for opt in options:
            opt['postproc'] = 0

        for seat in range(seats):
            counter = []
            for opt in options:
                r = opt['votes']/(opt['postproc']+1)
                counter.append(r)


            repeated = [x for x,y in collections.Counter(counter).items() if y>1]
            maxvalue = max(counter)
            maxoption = counter.index(maxvalue)
            if maxvalue in repeated:
                imaxvalue = [index for index, value in enumerate(repeated) if value==maxvalue]
                maxoption=-1
                mv = 0
                for i in imaxvalue:
                    maxvalue = options[i]['votes']
                    if maxvalue>=mv:
                        mv = maxvalue
                        maxoption = i


            options[maxoption]['postproc'] += 1

        return Response(options)

    def post(self, request):
        """
         * type: IDENTITY | DHONT
         * options: [
            {
             option: str,
             number: int,
             votes: int,
             ...extraparams
            }
           ]
        """

        t = request.data.get('type', 'IDENTITY')
        opts = request.data.get('options', [])
        seats = request.data.get('seats',0)

        if t == 'IDENTITY':
            return self.identity(opts)
        
        else:
            return self.dhont_method(options=opts, seats=seats)

        return Response({})
