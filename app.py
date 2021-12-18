import streamlit as st
import pandas as pd

from analysis import get_matchplc,do_plot_match,df2list
from checkrule import searchByName, searchByItem,get_rule_data
from utils import get_folder_list, get_section_list

rulefolder = 'rules'


def main():

    st.subheader("监管要求匹配分析")

    industry_list = get_folder_list(rulefolder)

    industry_choice = st.sidebar.selectbox('选择行业:', industry_list)

    if industry_choice != '':

        name_text = ''
        plc_val, plc_list = searchByName(name_text, industry_choice)

        plc_choice = st.sidebar.multiselect('选择制度1:', plc_list)

        plc_section_list = get_section_list(plc_val, plc_choice)
        plc_column_ls = st.sidebar.multiselect('选择制度1章节:',
                                                plc_section_list)
        if plc_column_ls == []:
            column_plc = ''
        else:
            column_plc = '|'.join(plc_column_ls)

        rule_val, rule_list = searchByName(name_text, industry_choice)

        rule_list = rule_val['监管要求'].drop_duplicates()
        rule_choice = st.sidebar.multiselect('选择制度2:', rule_list)

        rule_section_list = get_section_list(rule_val, rule_choice)
        rule_column_ls = st.sidebar.multiselect('选择制度2章节:',
                                                rule_section_list)
        if rule_column_ls == []:
            column_rule = ''
        else:
            column_rule = '|'.join(rule_column_ls)

        top = st.sidebar.slider('匹配条款数量选择',
                                min_value=1,
                                max_value=10,
                                value=3)

        if (plc_choice != []) & (rule_choice != []):

            plcdf, plc_embeddings = get_rule_data(plc_choice,
                                                    industry_choice)

            ruledf, rule_embeddings = get_rule_data(
                rule_choice, industry_choice)

            querydf, _ = searchByItem(plcdf, plc_choice, column_plc, '')
            # get index of rule
            plc_index = querydf.index.tolist()
            query_embeddings = plc_embeddings[plc_index]

            sentencedf, _ = searchByItem(ruledf, rule_choice, column_rule,
                                            '')
            # get index of rule
            rule_index = sentencedf.index.tolist()
            sentence_embeddings = rule_embeddings[rule_index]

            validdf = get_matchplc(querydf, query_embeddings, sentencedf,
                                    sentence_embeddings, top)

            combdf = pd.concat([querydf.reset_index(drop=True), validdf],
                                axis=1)

            x = st.sidebar.slider('匹配阈值选择%',
                                    min_value=0,
                                    max_value=100,
                                    value=80)
            st.sidebar.write('匹配阈值:', x / 100)
            match = st.sidebar.radio('条款匹配分析条件', ('查看匹配条款', '查看不匹配条款'))

            st.sidebar.write('制度1: ', '/'.join(plc_choice))
            st.sidebar.write('制度1章节: ', column_plc)
            st.sidebar.write('制度2: ', '/'.join(rule_choice))
            st.sidebar.write('制度2章节: ', column_rule)

            if match == '查看匹配条款':
                combdf['是否匹配'] = (combdf['匹配度'] >= x / 100).astype(int)
            else:
                combdf['是否匹配'] = (combdf['匹配度'] < x / 100).astype(int)

            do_plot_match(combdf, match)

            sampledf = combdf.loc[
                combdf['是否匹配'] == 1,
                ['监管要求', '结构', '条款', '匹配条款', '匹配章节', '匹配制度', '匹配度']]

            # calculate the percentage of matched items
            matchrate = sampledf.shape[0] / combdf.shape[0]
            st.sidebar.write('匹配率:', matchrate)
            st.sidebar.write('总数:', sampledf.shape[0], '/',
                                combdf.shape[0])
            dis1ls, dis2ls, dis3ls = df2list(sampledf)
            # enumerate each list with index
            for i, (dis1, dis2,
                    dis3) in enumerate(zip(dis1ls, dis2ls, dis3ls)):
                st.info('序号' + str(i + 1) + ': ' + dis1)
                st.warning(dis2)
                st.table(dis3)
            # analysis is done
            st.sidebar.success('分析完成')
            st.sidebar.download_button(label='下载结果',
                                data=sampledf.to_csv(),
                                file_name='分析结果.csv',
                                mime='text/csv')


if __name__ == '__main__':
    main()