from sentence_transformers import SentenceTransformer
import torch
import torch.nn as nn
from loguru import logger
import sys
logger.remove()  # Remove the default logger
logger.add(sys.stderr, level="DEBUG")  # Set level to DEBUG for console
# contains classes that compose the UI embedding model
class UIEmbedder(nn.Module):
    """
    Model intended to semantically embed the content of a UI element into a vector
    """
    def __init__(self, bert, bert_size=768, num_classes=26, class_emb_size=6):
        super().__init__()
        self.text_embedder = bert
        self.UI_embedder = nn.Embedding(num_classes, class_emb_size)
        self.bert_size = bert_size
        self.class_size = class_emb_size

    # embed ui_text and ui_class tag into a vector
    # ui_texts: a list contains the texts of ui elements
    # ui_class_tags: a tensor that contains class tags of ui elements
    def forward(self, ui_texts, ui_class_tags):
        logger.debug(f'ui_texts: {ui_texts}, ui_class_tags: {ui_class_tags}')
        text_emb = torch.as_tensor(self.text_embedder.encode(ui_texts))
        class_emb = self.UI_embedder(ui_class_tags)
        logger.debug(f'text_emb: {text_emb}, class_emb: {class_emb}')
        x = torch.cat((text_emb, class_emb), 1) # merge each element in text_emb and class_emb, keep element number unchanged
        for index in range(len(ui_texts)):
            if ui_texts[index] == '':
                x[index] = torch.zeros(self.bert_size + self.class_size)
        return x

class UI2Vec(nn.Module):

    """
    Model that wraps the UI Embedder
    """

    def __init__(self, bert, bert_size=768, num_classes=26, class_emb_size=6):
        """
        describe params here
        """
        super().__init__()
        self.embedder = UIEmbedder(bert, bert_size, num_classes)
        self.lin = nn.Linear(bert_size + class_emb_size, bert_size)
        try:
            self.lin.cuda()
        except Exception as inst:
            print(f'UI2Vec:init() {inst}')
            self.lin.cpu()

    # input [ui_text:list, ui_class_tag:tensor]
    # map a UI abstract list (a node and its all direct and indirect children) to a vector
    def forward(self, input_word_labeled):
        """
        describe params here
        """
        input_ui_texts = input_word_labeled[0]
        input_ui_class_tags = input_word_labeled[1]
        logger.debug(f'input_word_labeled: {input_word_labeled}, input_ui_class_tags: {input_ui_class_tags}, input_ui_texts: {input_ui_texts}')
        try:
            input_vector = self.embedder(input_ui_texts, input_ui_class_tags).cuda()
        except Exception as e:
            input_vector = self.embedder(input_ui_texts, input_ui_class_tags).cpu()
        logger.debug(f'input_vector: {input_vector} which was embedded from\ninput_ui_texts = {input_ui_texts}\ninput_ui_class_tags = {input_ui_class_tags}')
        output = self.lin(input_vector)
        logger.debug(f'output: {output}')
        return output

class HiddenLabelPredictorModel(nn.Module):
    """
    combines the n closest UI elements (text plus class) to predict the embedding
    of a different one on the same screen
    """
    def __init__(self, bert, bert_size, n, class_emb_size=6, num_classes=26):
        super().__init__()
        self.class_emb_size = class_emb_size
        self.lin = nn.Linear(bert_size*n, bert_size+ self.class_emb_size)
        try:
            self.lin.cuda()
        except Exception as inst:
            print(f'HiddenLabelPredictorModel:init() {inst}')
            self.lin.cpu()
        self.model = UI2Vec(bert)
        self.n = n
        self.bert_size = bert_size
        self.num_classes = num_classes

    def forward(self, context):
        # add all of the embedded texts into a megatensor
        # if missing (less than n)- add padding
        text_embedding = self.model(context[0])
        for index in range(1, self.n):
            to_add = self.model(context[index])
            text_embedding = torch.cat((text_embedding, to_add),1)
        return self.lin(text_embedding)