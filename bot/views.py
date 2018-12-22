from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *
from chatterbot import ChatBot
from bs4 import BeautifulSoup
import random
import requests


chatbot = ChatBot(
    'Jack',
    tie_breaking_method="random_response",
    trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
    read_only=True, # ensure model will not be affected after training
    logic_adapters=[
        "chatterbot.logic.MathematicalEvaluation",
        "chatterbot.logic.BestMatch",
        #{
        #    'import_path': 'chatterbot.logic.LowConfidenceAdapter',
        #    'threshold': 0.25,
        #    'default_response': '聽不懂你在說啥～我只是一個可愛的小Bot！'
        #}
    ],
)

low_confidence_reply = ['聽不懂你在說啥～我只是一個可愛的小Bot！',
                        '你說啥呢？我只知道我的主人是Jack Chen',
                        '我小小的腦袋無法了解> <，非常抱歉！',
                        '呀 還是聽不懂，不然我說個笑話好了：\n思思的帳號被冒用她的男友知道了以後很憤怒的說：可...可惡敢冒用思思',
                        '呀 還是聽不懂，不然我說個笑話好了：\n朋友：借我三千急用！！\n我：這我必須跟我女朋友商量一下。\n朋友：你不是沒有女朋友？\n我：所以沒得商量。',
                        '呀 還是聽不懂，不然我說個笑話好了：\n剛剛去買飲料路上遇到一群8+9\n其中一個對我說你知道我是誰嗎\n好可憐喔怎麼連自己是誰都忘了']

# Train based on the chinese and english corpus
#chatbot.train("chatterbot.corpus.chinese")
#chatbot.train("chatterbot.corpus.english.greetings")
#chatbot.train("chatterbot.corpus.english.conversations")
#chatbot.train("chatterbot.corpus.english.emotion")

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            print(event) # for debug
            if event.message.type == 'text':
                handle_text_message(event, chatbot)
            elif event.message.type == 'sticker':
                handle_sticker_message(event)

        return HttpResponse()
    else:
        return HttpResponseBadRequest()

def handle_text_message(event, chatbot):
    if event.message.text == "顯示選單":
        buttons_template = TemplateSendMessage(
            alt_text='顯示選單 template',
            template=ButtonsTemplate(
                title='想從什麼角度了解Jack Chen?',
                text='請選擇',
                thumbnail_image_url='https://drive.google.com/uc?export=view&id=1ukmT4NAxwqP3scF4MOry885CaAY8fg0r',
                actions=[
                    MessageTemplateAction(label='學業表現及簡介', text='學業表現及簡介'),
                    MessageTemplateAction(label='論文著述', text='論文著述'),
                    MessageTemplateAction(label='校外競賽', text='校外競賽'),
                    MessageTemplateAction(label='課外活動', text='課外活動')
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template)
    elif event.message.text == "論文著述":
        Carousel_template = TemplateSendMessage(
            alt_text='Carousel template',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url='https://i.imgur.com/T7tcYbk.jpg',
                        title='PhrecSys',
                        text='AAAI 2019 Workshop RecNLP',
                        actions=[
                            MessageTemplateAction(
                                label='簡介',
                                text='PhrecSys'
                            ),
                            URITemplateAction(
                                label='論文連結',
                                uri='https://arxiv.org/abs/1812.01808'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://i.imgur.com/eqXplQs.jpg',
                        title='MSG Recommender',
                        text='ICDE 2019 (Submitted)',
                        actions=[
                            MessageTemplateAction(
                                label='簡介',
                                text='MSG'
                            ),
                            URITemplateAction(
                                label='論文連結',
                                uri='https://goo.gl/UQCbWd'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://drive.google.com/uc?export=view&id=1upAJh8qGskQvZAIIJNV-W8zAu4Sgnx0B',
                        title='PGA Recommender',
                        text='WWW 2019 (Submitted)',
                        actions=[
                            MessageTemplateAction(
                                label='簡介',
                                text='PGA'
                            ),
                            URITemplateAction(
                                label='論文連結',
                                uri='https://goo.gl/8qBbrs'
                            )
                        ]
                    ),
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,Carousel_template)
    elif event.message.text == "PhrecSys":
        chat_response = 'In PhrecSys, we utilize phrase-level feature to enrich article recommender and use attention mechanism to demonstrate the merit of using phrases instead of words.'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=chat_response)
        )
    elif event.message.text == "MSG":
        chat_response = 'In MSG, we incorporate session information through skip-gram loss with original hinge loss in a multitask optimization manner, and boost all the content-based models.'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=chat_response)
        )
    elif event.message.text == "PGA":
        chat_response = 'In Phrased-Guided Attention, we try to mimic human reading behavior using key-term to attention on content, finally generate the aggregating article information.'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=chat_response)
        )
    elif event.message.text == '學業表現及簡介':
        chat_response = '家煒畢業於交通大學電子工程學系，累積排名: 3\nOverall GPA\t: 4.14\nMajor GPA\t\t: 4.18\nCS related GPA: 4.24\n4次書卷獎\n2017 林熊徵學田獎學金\n2018 殷之同學長電子實驗獎學金。'
        chat_response += '\n===================\n'
        chat_response += '擅長的程式語言：\nPython, C, C++, Shell'
        chat_response += '\n===================\n'
        chat_response += '擅長的能力：Machine Learning, Data Mining, Deep Learning, Natural Language Processing'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=chat_response)
        )
    elif event.message.text == "校外競賽":
        Carousel_template = TemplateSendMessage(
            alt_text='Carousel template',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url='https://drive.google.com/uc?export=view&id=1rvkxrV0ZU3PE70P_89LZ44rqx8EHL_Y2',
                        title='Smart Plate - 佳作',
                        text='2017 Synopsys ARC Design Contest',
                        actions=[
                            MessageTemplateAction(
                                label='簡介',
                                text='Smart Plate'
                            ),
                            URITemplateAction(
                                label='作品連結',
                                uri='https://drive.google.com/open?id=1wL9Hh_FJHyVrEds1cpOTEgIO2xfrn2Fl'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://drive.google.com/uc?export=view&id=1atw1SN1yGDqiNUMXUNwikr14jc_d8Z0f',
                        title='Elderly Saver - 佳作',
                        text='2017 MobileHero IoT Competition',
                        actions=[
                            MessageTemplateAction(
                                label='簡介',
                                text='Elderly Saver'
                            ),
                            URITemplateAction(
                                label='作品連結',
                                uri='https://github.com/ss87021456/2017-MobileHero_MTK'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://drive.google.com/uc?export=view&id=1IxQxDDGyi44F_Tif0BgGcubFzfP3TBNo',
                        title='揪Ｉ打球 - 佳作',
                        text='2017 MorSensor IoT Competition',
                        actions=[
                            MessageTemplateAction(
                                label='簡介',
                                text='Basket Predictor'
                            ),
                            URITemplateAction(
                                label='作品連結',
                                uri='https://github.com/ss87021456/Basketball_Shooting_Machine_Learning'
                            )
                        ]
                    ),
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,Carousel_template)
    elif event.message.text == "Smart Plate":
        chat_response = 'In Smart Plate, we implemented a product for users to track their daily food consumption information based on Synopsys ARC Processor, and transmit data through bluetooth/wifi.'
        chat_response += '\n在智慧餐盤裡，我們利用Synopsys ARC Processor幫助我們完成紀錄使用者每日飲食資訊，並可透過藍芽傳輸給手機，或Wifi傳輸給雲端。'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=chat_response)
        )
    elif event.message.text == "Elderly Saver":
        chat_response = 'In Elderly Saver, we designed the prototype of tracking shopping cart using object detection and a wearable device for elderly to monitor their health condition and relief their effort of pulling cart.'
        chat_response += '\n在長者安全救星裡，我們實做了一個產品雛型，利用影像物件追蹤老人，以及心跳感應器即時紀錄，讓老人可以安心出門買菜。'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=chat_response)
        )
    elif event.message.text == "Basket Predictor":
        chat_response = 'In Basket Predictor, we built a app and a wearable device that help people to predict basketball shootingbased on support vector machine with feature engineering.'
        chat_response += '\n在揪Ｉ打球裡，我們利用六軸感測數據並透過Machine Learning判斷，輸出投籃結果讓使用者了解練習狀況。'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=chat_response)
        )
    elif event.message.text == "課外活動":
        Carousel_template = TemplateSendMessage(
            alt_text='ImageCarousel template',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://drive.google.com/uc?export=view&id=1cf9N-W3bWjDWXQxAuwpgOvgYfluHrUZ-',
                        action=MessageAction(
                                label='簡介',
                                text='2014腳踏車環島',
                            )
                    ),
                    ImageCarouselColumn(
                        image_url='https://drive.google.com/uc?export=view&id=12bN4qBaWaXjGczcJMTImz8A3W6y9jFI6',
                        action=MessageAction(
                                label='簡介',
                                text='2015北電盃',
                            )
                    ),
                    ImageCarouselColumn(
                        image_url='https://drive.google.com/uc?export=view&id=1vnvgJAWwRldC7ULm9Obito-VhpK01Ccc',
                        action=MessageAction(
                                label='簡介',
                                text='2016大電盃',
                            )
                    ),
                    ImageCarouselColumn(
                        image_url='https://drive.google.com/uc?export=view&id=1Nvsl2M8kVmXrOhoYuTPUr-WHkfmr4_ik',
                        action=MessageAction(
                                label='簡介',
                                text='2017交大畢聯盃',
                            )
                    ),
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token,Carousel_template)
    elif event.message.text == "2014腳踏車環島":
        chat_response = '2014腳踏車環島，是Jack升大學的暑假，跟一群高中死黨，不怕死一起騎腳踏車環島，過程中我還因為防曬油沒有勤補而在屏東進了急診室，非常熱血好玩的一段旅程！'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=chat_response)
        )
    elif event.message.text == "2015北電盃":
        chat_response = '2015北電盃，是Jack大二時的杯賽，第一次參加電盃比賽，當時因為學長受傷的關係，擔任先發控球而且是隊上的得分王(平均6.5分)，最後打進了16強循環賽！'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=chat_response)
        )
    elif event.message.text == "2016大電盃":
        chat_response = '2016大電盃，是Jack大二下時，且第二次參加電盃比賽，同樣擔任先發控球，可惜籤運不佳，預賽進入死亡之組，最後一戰在落後15分的情況下，追到只差2分，卻還是被當年度第三名的隊伍給淘汰了。'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=chat_response)
        )
    elif event.message.text == "2017交大畢聯盃":
        chat_response = '2017交大畢聯盃，是Jack在大學最後一個比賽，這次比賽一路過關斬將，最後獲得了第三名的殊榮，算是給大學籃球留下一個美好的回憶。'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=chat_response)
        )
    elif event.message.text == "功能簡述":
        chat_response = '點選顯示選單可以看到主要功能（學業表現、論文著述、校外競賽、課外活動）'
        chat_response += '==================='
        chat_response += '\n圖文選單另有提供履歷(pdf)、美國交換心得(影片)\n'
        chat_response += '==================='
        chat_response += '\n其他回覆會統一由後台的『ChatterBot』代為回覆！'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=chat_response)
        )
    else:
        response = chatbot.get_response(event.message.text)
        confidence = response.confidence
        if confidence < 0.25:
            response.text = random.choice(low_confidence_reply)
            response.confidence = 1
        chat_response = '[ChatterBot with {:2.2f}% confidence]: \n{}'.format(100*response.confidence, response.text)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=chat_response)
        )

def handle_sticker_message(event):
    # ref. https://developers.line.me/media/messaging-api/sticker_list.pdf
    print("package_id:", event.message.package_id)
    print("sticker_id:", event.message.sticker_id)
    sticker_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 21, 100, 101, 102, 103, 104, 105, 106,
                   107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125,
                   126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 401, 402]
    index_id = random.randint(0, len(sticker_ids) - 1)
    sticker_id = str(sticker_ids[index_id])
    print(index_id)
    sticker_message = StickerSendMessage(
        package_id='1',
        sticker_id=sticker_id
    )
    line_bot_api.reply_message(
        event.reply_token,
        sticker_message)