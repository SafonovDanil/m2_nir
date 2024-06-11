Примеры:
# cpp_code = """
# struct ListNode {
#     int nValue;
#     ListNode* nx;
# };

# void initialize(ListNode* pNode, ListNode* pNextInit, int nValInit) {
#     pNode->nx = pNextInit;
#     pNode->nValue = nValInit;
# }

# int main() {
#     struct NodeInt* elemH = nullptr;
#     struct NodeInt* tmp = nullptr;
#     for(int i = 0; i < 2; i++)
#     {
#         tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#         initialize(tmp, nullptr, i);
#         elemH = tmp;
#     }
#     tmp = nullptr
# }
# """

# cpp_code = """
# struct ListNode {
#     int nValue;
#     ListNode* nx;
# };

# void initialize(ListNode* pNode, ListNode* pNextInit, int nValInit) {
#     pNode->nx = pNextInit;
#     pNode->nValue = nValInit;
# }

# int main() {
#     struct NodeInt* elemH = nullptr;
#     struct NodeInt* tmp = nullptr;
#     for(int i = 0; i < 2; i++)
#     {
#         tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#         initialize(tmp, elemH, i);
#         elemH = tmp;
#     }
#     tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#     initialize(tmp, elemH, 3);
#     tmp = nullptr
# }
# """

# cpp_code = """
# struct ListNode {
#     int nValue;
#     ListNode* nx;
# };

# void initialize(ListNode* pNode, ListNode* pNextInit, int nValInit) {
#     pNode->nx = pNextInit;
#     pNode->nValue = nValInit;
# }

# int main() {
#     struct NodeInt* elemH = nullptr;
#     struct NodeInt* tmp = nullptr;
#     for(int i = 0; i < 2; i++)
#     {
#         tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#         initialize(tmp, elemH, i);
#         elemH = tmp;
#     }
#     tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#     initialize(tmp, elemH, 3);
#     elemH = tmp;
#     tmp = nullptr
# }
# """

# cpp_code = """
# struct ListNode {
#     int nValue;
#     ListNode* nx;
# };

# void initialize(ListNode* pNode, ListNode* pNextInit, int nValInit) {
#     pNode->nx = pNextInit;
#     pNode->nValue = nValInit;
# }

# int main() {
#     struct NodeInt* elemH = nullptr;
#     struct NodeInt* tmp = nullptr;
#     tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#     initialize(tmp, nullptr, 10);
#     elemH = tmp;
#     tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#     if(elemH == nullptr){
#          initialize(tmp, elemH, 20);
#          elemH = tmp;
#     }
#     tmp = nullptr
# }
# """
# int main() {
#     int i = 0;
#     struct NodeInt* elemH = nullptr;
#     struct NodeInt* tmp = nullptr;
#     tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#     initialize(tmp, nullptr, 10);
#     elemH = tmp;
#     tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#     if(i == 0){
#          initialize(tmp, elemH, 20);
#          elemH = tmp;
#     }
#     tmp = nullptr
# }
# """
# cpp_code = """
# struct ListNode {
#     int nValue;
#     ListNode* nx;
# };

# void initialize(ListNode* pNode, ListNode* pNextInit, int nValInit) {
#     pNode->nx = pNextInit;
#     pNode->nValue = nValInit;
# }

# int main() {
#     struct NodeInt* elemH = nullptr;
#     struct NodeInt* tmp = nullptr;
#     tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#     initialize(tmp, nullptr, 10);
#     elemH = tmp;
#     tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#     initialize(tmp, elemH, 20);
#     tmp = nullptr
# }
# """
# cpp_code = """
# struct ListNode {
#     int nValue;
#     ListNode* nx;
# };

# void initialize(ListNode* pNode, ListNode* pNextInit, int nValInit) {
#     pNode->nx = pNextInit;
#     pNode->nValue = nValInit;
# }

# int main() {
#     struct NodeInt* elemH = nullptr;
#     struct NodeInt* tmp = nullptr;
#     tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#     initialize(tmp, nullptr, 10);
#     elemH = tmp;
#     tmp = (struct NodeInt*)malloc(sizeof(struct NodeInt));
#     initialize(tmp, elemH, 20);
#     elemH = tmp;
#     tmp = nullptr
# }
# """
